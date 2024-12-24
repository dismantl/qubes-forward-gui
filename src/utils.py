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

def get_qubes() -> list[Qube]:
    if os.environ.get('PYTHONHOME'):
        del os.environ['PYTHONHOME']
    if config.dev:
        with open('assets/qvm-ls.txt', 'r') as f:
            text = f.read()
    else:
        config.logger.debug("dom0 executing `qvm-ls`")
        stdout, stderr = Popen(["qvm-ls"], stdout=PIPE, stderr=PIPE).communicate()
        config.logger.debug(f"dom0: `qvm-ls` stdout:\n{stdout.decode()}")
        config.logger.debug(f"dom0: `qvm-ls` stderr:\n{stderr.decode()}")
        text = stdout.decode()
    
    qubes: list[Qube] = []
    text = text.strip()
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
    
    config.logger.debug(f"qubes list: {qubes}")
    return qubes

def get_qubes_running() -> list[Qube]:
    qubes = get_qubes()
    running = [q for q in qubes if q.status == "Running" and q.name != "dom0"]
    config.logger.debug(f"running qubes list: {running}")
    return running

def add_forward_rule(from_qube: str, from_port: int, to_qube: str, to_port: int) -> database.ForwardRule:
    if os.environ.get('PYTHONHOME'):
        del os.environ['PYTHONHOME']
    rule: database.ForwardRule = database.ForwardRule.create(
        from_qube=from_qube, 
        from_port=from_port, 
        to_qube=to_qube, 
        to_port=to_port
    )
    if config.dev:
        config.logger.debug("config.dev enabled, command didn't executed")
    else:
        command = f"qvm-run -u root --pass-io {to_qube} qvm-connect-tcp {to_port}:{from_qube}:{from_port}"
        config.logger.debug(f"dom0 executing `{command}`")
        stdout, stderr = Popen(["timeout", "2",
            "qvm-run", "-u", "root", "--pass-io", to_qube, 
            f"qvm-connect-tcp {to_port}:{from_qube}:{from_port}"
            ], stdout=PIPE, stderr=PIPE).communicate()

        config.logger.debug(f"dom0 command `{command}` stdout:\n{stdout.decode()}")
        config.logger.debug(f"dom0 command `{command}` stdout:\n{stderr.decode()}")
    return rule

def get_open_ports(qube: str) -> list[Port]:
    if os.environ.get('PYTHONHOME'):
        del os.environ['PYTHONHOME']
    if config.dev:
        with open('assets/ss-tlpn.txt', 'r') as f:
            text = f.read()
        config.logger.debug(text)            
    else:
        config.logger.debug(f"dom0 execute `qvm-run -u root --pass-io {qube} 'ss -tlpn'`")
        stdout, stderr = Popen(["qvm-run", "-u", "root", "--pass-io", qube, "ss -tlpn"], stdout=PIPE, stderr=PIPE).communicate()
        config.logger.debug(f"dom0 command stdout:\n{stdout.decode()}")
        config.logger.debug(f"dom0 command stderr:\n{stderr.decode()}")
        text = stdout.decode()
        
    ports: list[Port] = []
    text = text.strip()
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
    if os.environ.get('PYTHONHOME'):
        del os.environ['PYTHONHOME']
    rule: database.ForwardRule = database.ForwardRule.get_by_id(rule_id)
    if not config.dev:
        config.logger.debug(f"dom0 cmd: qvm-run -u root {rule.to_qube} 'kill {rule.pid}'")
        stdout, stderr = Popen(["qvm-run", "-u", "root", rule.to_qube, f"kill {rule.pid}"], stdout=PIPE, stderr=PIPE).communicate()
        config.logger.debug(f"dom0 command stdout:\n{stdout.decode()}")
        config.logger.debug(f"dom0 command stderr:\n{stderr.decode()}")
    rule.delete_instance()

if __name__ == '__main__':
    config.debug = True
    config.dev = True
    config.logger.add(sys.stdout, level="DEBUG")

    get_forward_rules()