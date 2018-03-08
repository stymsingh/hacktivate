import hashlib as hasher
import json
from flask import Flask, jsonify, request
from uuid import uuid4
"""
Block structure:- 
index,timestamp,previousHash,hash,transactions,balance,chain,nodes,email,lat,long,energy,unit
"""



class Block:
    def __init__(self,index,timestamp,previousHash,email,lat,long,energy,unit):
        self.index = index
        self.timestamp = timestamp
        self.previousHash = previousHash
        self.balance = float(100)
        self.email = email
        self.lat = float(lat)
        self.long = float(long)
        self.energy = float(energy)
        self.unit = float(unit)
        self.hash = self.calculateHash()
        # self.current_transactions = []


    def calculateHash(self):
        block = {
            'index':self.index,
            'timestamp': self.timestamp,
            'previousHash': self.previousHash,
            'email':self.email,
            'lat':self.lat,
            'long':self.long,
            'energy':self.energy,
            'unit': self.unit
        }
        encrypt = json.dumps(block,sort_keys=True).encode()
        return hasher.sha256(encrypt).hexdigest()


class Blockchain:
    def __init__(self):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        gene = Block(index=0,timestamp='01/01/2017',previousHash='',email='super@blockchain.com',lat=0.0,long=0.0,energy=100,unit=10)
        self.chain.append(gene)

    def create_new_node(self,timestamp,email,lat,long,energy,unit):
        block = Block(index=len(self.chain)+1,timestamp=timestamp,previousHash=self.chain[-1].hash,email=email,lat=lat,long=long,energy=energy,unit=unit)
        self.chain.append(block)
        self.nodes.add(block)
        if self.checkValidity(block):
            return block
        else:
            return 0

    def Chain(self):
        return self.chain

    def transaction(self,sender_id,reciever_id,amount,energy):
        if sender_id == reciever_id:
            print("Same hashes")
            return 0
        sender = None
        reciever = None
        for i in self.chain:
            print(i.email)
            if i.hash == sender_id and sender == None:
                print("Sender found")
                sender = i
                i.balance += float(amount)
                i.energy -= float(energy)
            if i.hash == reciever_id and reciever == None:
                print("Reciever Found")
                reciever = i
                i.balance -= float(amount)
                i.energy += float(energy)
            if sender != None and reciever != None:
                print("{} recieved {} energy from {} amounting {}".format(reciever.email,sender.email,energy,amount))
                data = {'sender':sender_id,'reciever':reciever_id,'amount':amount,'energy':energy}
                self.transactions.append(data)

                return 1
        print("Transaction not possible",sender.email,reciever.email)
        return 0

    def search(self,id):
        for i in self.chain:
            if i.hash == id:
                return {'email':i.email,'amount':i.balance,
                        'energy':i.energy}
        return "NOT FOUND"

    def length(self):
        return len(self.chain)

    def avg_price(self):
        ans = 1.0
        tot = 0.0
        for i in self.chain:
            tot+= i.unit
        ans = ans*tot/self.length()
        return ans

    def last_block(self):
        return self.chain[-1].email

    def checkValidity(self,node):
        chai = self.chain
        for i in range(1,len(chai)):
            if chai[i] == node:
                if chai[i].previousHash == chai[i-1].hash:
                    return True

        return False



# import datetime
# basic = Blockchain()
# basic.create_new_node(timestamp=str(datetime.datetime.now()),email="super2@gmail.com",lat=0.22,long=0.22,energy=100)
# Instantiate the Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/add/', methods=['GET'])
def add_block():
    # timestamp,email,lat,long,energy
    timestamp = request.args.get('timestamp')
    email = request.args.get('email')
    lat = request.args.get('lat')
    long = request.args.get('long')
    energy = request.args.get('energy')
    unit = request.args.get('unit')
    block = blockchain.create_new_node(email=email,timestamp=timestamp,
                               lat=lat,long=long,energy=energy,unit=unit)
    if block == 0:
        response = {
            'message':"Node cannot be added",
        }
        return jsonify(response), 200

    print("Node {} successfully added".format(block.index))
    response = {
        'message': 'Node successfully added',
        'index': block.index,
        'previousHash':block.previousHash,
        'hash': block.hash
    }
    return jsonify(response), 200

@app.route('/chain',methods=['GET'])
def chainBlock():
    chain = [{'previousHash':x.previousHash,'hash':x.hash,'email':x.email,'lat':x.lat,'long':x.long,'energy':x.energy,'unit':x.unit,'balance':x.balance} for x in blockchain.Chain()]
    response = {
        'chain':chain,
    }
    return jsonify(response), 200


@app.route('/transaction/',methods=['GET'])
def transac():
    sender_hash = request.args.get('sen')
    reciever_hash = request.args.get('rec')
    energy = request.args.get('energy')
    amount = request.args.get('cost')

    flag = blockchain.transaction(sender_id = sender_hash,
                            reciever_id=reciever_hash,
                            energy= energy,
                            amount = amount)
    if flag == 0:
        response = {
            'message': "Error, something wrong"
        }
    else:
        response = {
            'transaction':blockchain.transactions[-1],
            'sender_details': blockchain.search(sender_hash),
            'reciever_details': blockchain.search(reciever_hash)
        }

    return jsonify(response), 200

@app.route('/chainLength/',methods=['GET'])
def chainlength():
    response = {
        'length':blockchain.length()
    }
    return jsonify(response), 200

@app.route('/avg/',methods=['GET'])
def avgprice():
    response = {
        'avg_price': blockchain.avg_price()
    }
    return jsonify(response), 200

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='localhost', port=port)




