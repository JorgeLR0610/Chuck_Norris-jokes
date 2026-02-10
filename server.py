import grpc
from concurrent import futures
import requests # I know requests is single-threaded, maybe I'll change it later to something asynchronus like aiohttp or httpx (?); oh but it seems like I would have to change the way I create the server too

import jokes_pb2, jokes_pb2_grpc

class ChuckNorrisService(jokes_pb2_grpc.ChuckNorrisServicer):
    
    # It seems like context is used to cancel requests, timeouts and send headers, although I don't use just now
    # Also, the parameter request is an instance of the class JokeRequest
    def GetJoke(self, request, context): 
        category = request.category # Use dot notation to access that attribute
        print(f"Request for category: {category}")

        try: # category would be a Falsy value if not category provided, since protobuf 3 would default to empty str, which is Falsy 
            if not category: 
                print("No category selected, fetching random joke")
                url: str = "https://api.chucknorris.io/jokes/random"
            else:
                url: str = "https://api.chucknorris.io/jokes/random?category={category}" # I know this is hardcoded, I should change it later
                
            response = requests.get(url)
            
            if response.status_code == 200:
                json_data = response.json() # Deserialize the response into a Python dict, so below, in json_data['value'], the value of that key is passed
                
                # So, here's where the JokeResponse object is returned, matching the atributes' names defined in protobuf file
                return jokes_pb2.JokeResponse( 
                    joke=json_data['value'], # value is the name of the key containing the joke, acording to their example response
                    success=True,
                    error_message=""
                )
                
            elif response.status_code == 404:
                return jokes_pb2.JokeResponse(
                    joke="No joke was found for that category, make sure it exists",
                    success=False,
                    error_message="404 Not found"
                )
            
            # In case the error code is other than 404
            else: 
                return jokes_pb2.JokeResponse(
                    joke="",
                    success=False,
                    error_message=f"Chuch Norris API failed with code: {response.status_code}"
                )
                
        except Exception as e:
            print(f"Internal error: {e}")
            return jokes_pb2.JokeResponse(
                joke="",
                success=False,
                error_message=str(e)
            )
       
def run_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    jokes_pb2_grpc.add_ChuckNorrisServicer_to_server(ChuckNorrisService(), server)
    
    server.add_insecure_port('[::]:50051')
    
    server.start()
    print("gRPC server listening on port 50051")
    
    server.wait_for_termination()
    
if __name__ == '__main__':
    run_server()