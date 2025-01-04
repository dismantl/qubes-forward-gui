from config import config
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor
import database
import re
import os
import sys
from subprocess import Popen, PIPE

@dataclass
class Qube:
    name: str
    status: str
    type: str
    color: str
    template: str
    net: str

@dataclass
class Port:
    state: str
    recv: int
    send: int
    local_addr: str
    local_port: int
    peer_addr: str
    peer_port: str
    process: None | int

@dataclass
class ShellResponse:
    command: list[str]
    stdout: str
    stderr: str

def dom0_shell(command: list[str]) -> ShellResponse:
    # fix pyinstaller bug
    if os.environ.get('PYTHONHOME'):
        del os.environ['PYTHONHOME']

    config.logger.debug(f"dom0 executing {command}")
    stdout, stderr = Popen(command, stdout=PIPE, stderr=PIPE).communicate()
    stdout = stdout.decode().strip()
    stderr = stderr.decode().strip()
    config.logger.debug(f"dom0 stdout:\n{stdout}")
    config.logger.debug(f"dom0 stderr:\n{stderr}")
    return ShellResponse(command, stdout, stderr)

def execute_or_read(file: str, command: list[str]) -> str:
    if config.dev:
        config.logger.debug(f"dev mode enabled, reading: {file}")
        with open(file, 'r') as f:
            text = f.read()
        config.logger.debug(f"file content:\n{text}")
        return text
    
    return dom0_shell(command).stdout

def get_qubes() -> list[Qube]:
    text = execute_or_read('assets/qvm-ls.txt', ["qvm-ls"])
    
    qubes: list[Qube] = []
    text = re.sub(' +', ' ', text)
    for i, line in enumerate(text.split('\n')):
        if i == 0:
            continue

        parts = line.split(' ')
        qube = Qube(
            parts[0], parts[1],
            parts[2], parts[3],
            parts[4], parts[5]
        )
        qubes.append(qube)
    
    # config.logger.debug(f"qubes list: {qubes}")
    return qubes

def get_qubes_running() -> list[Qube]:
    qubes = get_qubes()
    running = [q for q in qubes if q.status == "Running" and q.name != "dom0"]
    # config.logger.debug(f"running qubes list: {running}")
    return running

def add_forward_rule(from_qube: str, from_port: int, to_qube: str, to_port: int) -> database.ForwardRule:
    rule: database.ForwardRule = database.ForwardRule.create(
        from_qube=from_qube, 
        from_port=from_port, 
        to_qube=to_qube, 
        to_port=to_port
    )
    if config.dev:
        config.logger.debug("config.dev enabled, command didn't executed")
    else:
        dom0_shell([
            "timeout", "1",
            "qvm-run", "-u", "root", "--pass-io", to_qube, f"qvm-connect-tcp {to_port}:{from_qube}:{from_port}"
        ])
    return rule

def get_open_ports(qube: str) -> list[Port]:
    text = execute_or_read(
        'assets/ss-tlpn.txt', 
        ["timeout", "1", "qvm-run", "-u", "root", "--pass-io", qube, "ss -tlpn"]
    )
        
    ports: list[Port] = []
    text = re.sub(' +', ' ', text)
    for i, line in enumerate(text.split('\n')):
        if i == 0:
            continue
        
        parts = line.split(' ')
        local_parts = parts[3].rsplit(':', 1)
        peer_parts = parts[4].rsplit(':', 1)
        try:
            pid = int(parts[5].split('pid=')[1].split(',')[0])
        except:
            pid = None

        ports.append(Port(
            state=parts[0],
            recv=int(parts[1]),
            send=int(parts[2]),
            local_addr=local_parts[0],
            local_port=int(local_parts[1]),
            peer_addr=peer_parts[0],
            peer_port=peer_parts[1],
            process=pid
        ))
    config.logger.debug(f"open ports in {qube}: {ports}")
    return ports
        

def get_forward_rules() -> list[database.ForwardRule]:
    valid_rules: list[database.ForwardRule] = []
    rules: list[database.ForwardRule] = database.ForwardRule.select()
    config.logger.debug(f"rules in database: {[r for r in rules]}")
    
    # filtering disabled qubes
    running_qubes = get_qubes_running()
    running_qubes_names = [q.name for q in running_qubes]
    filtered_rules: list[database.ForwardRule] = []
    for rule in rules:
        if rule.to_qube not in running_qubes_names:
            config.logger.warning(f"Qube {rule.to_qube} is shutdown, deleting rules for it")
            try: database.ForwardRule.delete().where(database.ForwardRule.to_qube==rule.to_qube).execute() # type: ignore
            except: pass
        else:
            filtered_rules.append(rule)
    
    qube_to_port: str[list[Port]] = {}
    filtered_qubes_names = list(set([r.to_qube for r in filtered_rules]))
    
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(get_open_ports, filtered_qubes_names))
        config.logger.debug(f"pool results: {results}")
        
    for i, qube_name in enumerate(filtered_qubes_names):
        qube_to_port[qube_name] = results[i]
    
    config.logger.debug(f"qube_to_port: {qube_to_port}")
    for rule in filtered_rules:
        ports: list[Port] = qube_to_port[rule.to_qube]
        for port in ports:
            if rule.to_port == port.local_port and (port.local_addr == '*' or port.local_addr == '0.0.0.0'):
                rule.pid = port.process
                rule.save()
                valid_rules.append(rule)
    
    valid_rules_ids = [r.id for r in valid_rules]
    for rule in filtered_rules:
        if rule.id not in list(set(valid_rules_ids)):
            config.logger.warning(f"Found invalid rule {rule.id}: {rule.from_qube}:{rule.from_port} => {rule.to_qube}:{rule.to_port}, deleting")
            database.ForwardRule.delete_by_id(rule.id)
    
    config.logger.debug(f"valid_rules: {valid_rules}")
    return valid_rules

def delete_forward_rule(rule_id: int):
    rule: database.ForwardRule = database.ForwardRule.get_by_id(rule_id)
    if not config.dev:
        dom0_shell(["timeout", "1", "qvm-run", "-u", "root", rule.to_qube, f"kill {rule.pid}"])
    rule.delete_instance()

@dataclass
class NftRule:
    proto: str
    port: int
    action: str

def get_nft_rules(qube: str) -> list[NftRule]:
    config.logger.debug(f"get nft rules for qube {qube}")
    text = execute_or_read(
        'assets/nft-chain.txt', 
        ["timeout", "1", "qvm-run", "-u", "root", "--pass-io", qube, "nft list chain ip qubes custom-input"]
    )
    rules: list[NftRule] = []
    text = text.replace('\t', '')
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # skip first and last 2 lines
        if i in [0, 1, len(lines)-1, len(lines)-2]:
            pass
        parts = line.split(' ')
        if len(parts) != 7:
            continue
        try: rules.append(NftRule(
                proto=parts[3],
                port=int(parts[5]),
                action=parts[6]
            ))
        except: pass
    config.logger.debug(f"nft rules in {qube}: {rules}")
    return rules

def get_firewall_rules() -> list[database.FirewallRule]:
    rules_db: list[database.FirewallRule] = database.FirewallRule.select()
    running_qubes = get_qubes_running()
    running_qubes_names = [q.name for q in running_qubes]
    for rule in rules_db:
        if rule.qube not in running_qubes_names:
            config.logger.warning(f"qube {rule.qube} is shutdown, deleting rule from database")
            rule.delete_instance()   
 
    rules_db: list[database.FirewallRule] = list(database.FirewallRule.select())
    uniq_qubes_names = list(set([r.qube for r in rules_db]))
    qube_to_nft: str[list[NftRule]] = {}

    with ProcessPoolExecutor() as executor:
        config.logger.debug(f"uniq_qubes_names: {uniq_qubes_names}")
        results = list(executor.map(get_nft_rules, uniq_qubes_names))
        config.logger.debug(f"pool results: {results}")

    for i, qube_name in enumerate(uniq_qubes_names):
        qube_to_nft[qube_name] = results[i]
    
    valid_rules: list[database.FirewallRule] = []
    for rule in rules_db:
        nft_rules: list[NftRule] = qube_to_nft[rule.qube]
        for nft_rule in nft_rules:
            if rule.port == nft_rule.port and nft_rule.action == 'accept':
                valid_rules.append(rule)

    config.logger.debug(f'valid firewall rules: {valid_rules}')
    return valid_rules

def add_firewall_rule(qube: str, port: int) -> database.FirewallRule:
    rule = database.FirewallRule.create(qube=qube, port=port)
    if config.dev:
        config.logger.warning(f'config.dev enabled, skipping add firewall rule {qube}:{port}')
    else:
        dom0_shell([
            "timeout", "1", "qvm-run", "-u", "root", "--pass-io", qube, 
            f"nft add rule ip qubes custom-input meta l4proto tcp ct state new,established tcp dport {port} accept"
        ])
    return rule

def delete_firewall_rule(rule_id: int):
    rule: database.FirewallRule = database.FirewallRule.get_by_id(rule_id)
    if config.dev:
        config.logger.warning(f'config.dev enabled, skipping delete firewall rule {rule.qube}:{rule.port}')
    else:
        dom0_shell([
            "timeout", "1", "qvm-run", "-u", "root", "--pass-io", rule.qube, 
            f"nft flush chain ip qubes custom-input"
        ])
    database.FirewallRule.delete().where(database.FirewallRule.qube == rule.qube).execute()

def get_rules(firewall: bool) -> list[database.FirewallRule | database.ForwardRule]:
    config.logger.debug(f"get_rules, firewall: {firewall}")
    if firewall:
        return get_firewall_rules()
    return get_forward_rules()

if __name__ == '__main__':
    config.debug = True
    config.dev = True
    config.logger.add(sys.stdout, level="DEBUG")

    get_nft_rules("personal")