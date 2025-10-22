import websocket
import json
import math

eth_close = None
btc_close = None
eth_btc_close = None




def weighted_graph(p1:float,p2:float,p3:float):
    '''p1 : ETH/btc p2 : ETH/USDT p3 : btc/USDT'''
    return {"ETH":{"btc":-math.log(p1),"USDT":-math.log(p2)},
            "btc":{"ETH":-math.log(1/p1),"USDT":-math.log(p3)},
            "USDT":{"ETH":-math.log(1/p2),"btc":-math.log(1/p3)}}
    

def check_arbitrage_optimized(p1, p2, p3,fee):
    """
    Checks the 3 possible triangular arbitrage cycles in the 3-node graph.
    Returns the cycle with the best profit if found, otherwise None.
    """

    # Calculate log weights directly to avoid intermediate graph creation overhead
    w1 = -math.log(p1 *(1-fee))       # ETH -> btc
    w2 = -math.log(p2*(1-fee))       # ETH -> USDT
    w3 = -math.log(p3*(1-fee))       # btc -> USDT
    w1_rev = -math.log((1/p1)*(1-fee)) # btc -> ETH
    w2_rev = -math.log((1/p2)*(1-fee)) # USDT -> ETH
    w3_rev = -math.log((1/p3)*(1-fee)) # USDT -> btc

    opportunities = []

    # Cycle 1: ETH -> btc -> USDT -> ETH
    # Weights: w1 + w3 + w2_rev
    cycle1_weight = w1 + w3 + w2_rev
    if cycle1_weight < 0:
        profit_rate = math.exp(-cycle1_weight)
        opportunities.append(('ETH->btc->USDT->ETH', cycle1_weight,profit_rate))

    # Cycle 2: ETH -> USDT -> btc -> ETH
    # Weights: w2 + w3_rev + w1_rev
    cycle2_weight = w2 + w3_rev + w1_rev
    if cycle2_weight < 0:
        profit_rate = math.exp(-cycle2_weight)
        opportunities.append(('ETH->USDT->btc->ETH', cycle2_weight,profit_rate))

    # The reverse cycles of the above two are just 0-sum if the rates are consistent
    # We only need to check these fundamental cycles.

    if opportunities:
        # Find the cycle with the smallest negative weight (highest potential profit)
        best_opportunity = min(opportunities, key=lambda x: x[1])
        return best_opportunity
    else:
        return None



def update_price(json_msg:dict):
    global eth_close,eth_btc_close,btc_close
    symbol = json_msg["data"]["s"]
    if symbol == "ETHUSDT" :
        eth_close = float(json_msg["data"]["c"])
    elif symbol == "BTCUSDT" :
        btc_close = float(json_msg["data"]["c"])
    else :
        eth_btc_close = float(json_msg["data"]["c"])
 

def on_message(ws,message):
    json_msg = json.loads(message)
    update_price(json_msg)
    if any(x is None for x in [eth_close, btc_close, eth_btc_close]):
        return
    
    # graph = weighted_graph(eth_btc_close,eth_close,btc_close)
    
    # print(graph)
    print(check_arbitrage_optimized(eth_btc_close,eth_close,btc_close,0.00075))

    
if __name__=="__main__":
    #CRYPTO CHOOSE btc BTC ETH 3 NODES GRAPH
    socket = "wss://stream.binance.com:9443/stream?streams=btcusdt@miniTicker/ethusdt@miniTicker/ethbtc@miniTicker"
    webs = websocket.WebSocketApp(socket,on_message=on_message)
    webs.run_forever()