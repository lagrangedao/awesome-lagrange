import os
import json
import requests
import random
import io
import base64
import time
import uuid
import traceback

from PIL import Image
from dotenv import load_dotenv
from web3 import HTTPProvider, Web3, Account
from web3.middleware import geth_poa_middleware

from swan_lag.api_client import APIClient
from swan_lag.api.lag_client import LagAPI

DEBUG = True

abi = '''[
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "sourceCode",
        "type": "string"
      },
      {
        "internalType": "bytes32",
        "name": "donId",
        "type": "bytes32"
      },
      {
        "internalType": "address",
        "name": "nftCollection",
        "type": "address"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "constructor"
  },
  {
    "inputs": [],
    "name": "EmptyArgs",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "EmptySource",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "NoInlineSecrets",
    "type": "error"
  },
  {
    "inputs": [],
    "name": "OnlyRouterCanFulfill",
    "type": "error"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "requestId",
        "type": "bytes32"
      }
    ],
    "name": "UnexpectedRequestID",
    "type": "error"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "id",
        "type": "bytes32"
      }
    ],
    "name": "RequestFulfilled",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "id",
        "type": "bytes32"
      }
    ],
    "name": "RequestSent",
    "type": "event"
  },
  {
    "anonymous": false,
    "inputs": [
      {
        "indexed": true,
        "internalType": "bytes32",
        "name": "requestId",
        "type": "bytes32"
      },
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "response",
        "type": "bytes"
      },
      {
        "indexed": false,
        "internalType": "bytes",
        "name": "err",
        "type": "bytes"
      }
    ],
    "name": "Response",
    "type": "event"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "name",
        "type": "string"
      }
    ],
    "name": "getResult",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "requestId",
        "type": "bytes32"
      },
      {
        "internalType": "bytes",
        "name": "response",
        "type": "bytes"
      },
      {
        "internalType": "bytes",
        "name": "err",
        "type": "bytes"
      }
    ],
    "name": "handleOracleFulfillment",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "name",
        "type": "string"
      }
    ],
    "name": "mint",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "name": "mintable",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "name": "nameToId",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "nftContract",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "name": "recipient",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "name": "result",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "s_lastError",
    "outputs": [
      {
        "internalType": "bytes",
        "name": "",
        "type": "bytes"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "s_lastRequestId",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "",
        "type": "bytes32"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "s_lastResponse",
    "outputs": [
      {
        "internalType": "bytes",
        "name": "",
        "type": "bytes"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      {
        "internalType": "string",
        "name": "name",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "desc",
        "type": "string"
      },
      {
        "internalType": "string",
        "name": "image_url",
        "type": "string"
      }
    ],
    "name": "sendRequest",
    "outputs": [
      {
        "internalType": "bytes32",
        "name": "requestId",
        "type": "bytes32"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "source",
    "outputs": [
      {
        "internalType": "string",
        "name": "",
        "type": "string"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]'''
def get_image(url='https://pgmwn8b5xu.meta.crosschain.computer',
              username='admin',password='admin1234',
              prompt='a green apple',negative_prompt='violent',
              sampler_name='Euler',
              seed=985454925,cfg_scale=5,steps=30,width=512,height=512):
    # Encode the username and password in Base64
    credentials = f'{username}:{password}'
    credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }
    # construct payload as a dictionary
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "sampler_name": sampler_name,
        "seed": seed,
        "cfg_scale": cfg_scale,
        "steps": steps,
        "width": width,
        "height": height,
    }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload, headers=headers)  
    try:
        r = response.json()  
        image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
        # image = image.resize((512,512))
    except Exception as e:
        print(e)
        raise Exception("Error getting image from diffusion model")
    return image


def save_to_MCS_bucket( bucket_name="diffusion2",file_path="output.png",name="output.png",
                       overwrite_file=False,initialize_bucket=True):
    from swan_mcs import APIClient,BucketAPI
    def initialize_client(api_key,chain="polygon.mumbai",):
        mcs_api = APIClient(api_key, chain  )
        return BucketAPI(mcs_api)
    bucket_client = initialize_client(api_key=os.getenv("MCS_API_KEY"))
    if initialize_bucket: bucket_client.create_bucket(bucket_name)   
    if overwrite_file:
        print(f"Overwriting file {name}")
        bucket_client.delete_file(bucket_name, name)
    file_data = bucket_client.upload_file(bucket_name, name , file_path) 
    if not file_data:
        print("upload failed")
        raise Exception("upload failed") 
    file_data = json.loads(file_data.to_json())
    print(file_data)
    return file_data["ipfs_url"]  


def upload_img2lag(img_file_path,dataset_name,is_public):
    
    #Sample files format
    files = {"file": (img_file_path, open(img_file_path, "rb"))}
    lag_client.create_dataset(dataset_name, is_public)
    #Upload_files_to_dataset
    res = lag_client.upload_dataset_file(dataset_name,files)
    if DEBUG:print(res)
    if res['status'] != 'success':
        raise Exception("Error uploading file to LAG")

def generate_prompt():
    # Generate a prompt for the diffusion model
    positive_prompt_pool = {
      "technology": [
        "Space Station", "Advanced Telescope", "Intergalactic Spacecraft", "Alien Observatory", 
        "Quantum Computer", "Hyperspace Engine", "Teleportation Device", "Force Field Generator", 
        "Nano Robots", "Time Machine", "Antimatter Reactor", "Orbital Habitat", "Deep Space Probe",
        "Dimensional Warp Machine", "Gravity Manipulator", "Interdimensional Portal", 
        "Cosmic Time Dial", "Asteroid Mining Rig", "Galactic Signal Array", 
        "Quantum Entanglement Communicator", "Stellar Forge", "Virtual Reality Construct", "Nanobot Swarm",
        "Starry Navigation System", "Orion's Belt Energy Harvester", "Pleiades Communication Network", "Andromeda Data Archive"
      ],
      "lighting": [
        "Stellar Glow", "Cosmic Ambient Light", "Supernova Explosion Light", "Bioluminescence", 
        "Auroral Light", "Reflection from Planetary Rings", "Laser Comms Beam", "Neutron Star Light", 
        "Dark Energy Glow", "Eclipse Shadow Light", "Quantum Light Echo", "Interstellar Aurora", 
        "Photon Storm Illumination", "Galactic Core Light", "Void Darkness Contrast", 
        "Time-Space Warp Glow", "Cosmic Ray Shimmer", "Parallel Universe Light",
        "Constellation Illumination Pattern", "Zodiacal Light Display", "Ursa Major Energy Emission", "Sirius Starlight Effect"
      ],
      "viewpoint": [
        "First Person View", "Aerial View", "View from a Spacecraft", "Telescope Zoom", 
        "Panoramic View", "Through an Alien's Eyes", "Microscopic Quantum Level", "Galactic Scale", 
        "Multiverse Perspective", "Inside a Black Hole", "Edge of the Universe", "Through a Wormhole", 
        "Dimensional Crossroads", "Nebula Core View", "Galactic Cluster Overview", 
        "Inside a Quantum Computer", "Celestial Observatory", "Futuristic Megacity Skyline",
        "Observing from a Constellation", "Milky Way Edge Perspective", "Through the Lens of Cassiopeia", "View from the Star Cluster"
      ],
      "colorScheme": [
        "Galactic Blues and Purples", "Nebula Reds and Oranges", "Cold Space Grays", 
        "Warm Planetary Yellows and Greens", "Alien Planet Pastels", "Black Hole Black and White", 
        "Quantum Fluctuation Hues", "Supernova Spectrum", "Dark Matter Shades", "Intergalactic Neon Spectrum", 
        "Quantum Superposition Colors", "Void and Star Contrast", "Exotic Alien Flora Colors", 
        "Dimensional Transition Shades", "Supernatural Aurora Palette", "Cosmic Dust Hues", 
        "Galactic Sunrise Tones", "Stellar Collapse Colors",
        "Celestial Constellation Hues", "Orion Nebula Color Palette", "Galactic Cluster Spectrum", "Andromedan Sky Tones"
      ],
      "SciFiObject": [
        "Futuristic Military Cyborg", "Advanced Spacecraft", "Alien Technology", "Interstellar Station", 
        "Quantum Device", "Extraterrestrial Artifact", "Robotic Drone", "Energy Shield", "Space Elevator", 
        "Artificial Moon", "Dimensional Key", "Cosmic Compass", "Galactic Atlas", "Stellar Map", 
        "Quantum Lock", "Time Continuum Navigator", "Celestial Codex", "Alien Energy Core", "Starforge Hammer",
        "Celestial Star Mapper", "Galaxy Pattern Decoder", "Constellation Energy Converter", "Orbiting Star Observatory"
      ],
      "SciFiEnvironment": [
        "Dystopian City", "Cyberpunk Streets", "Futuristic Metropolis", "Interstellar Space", 
        "Alien Landscape", "High-Tech Laboratory", "Underground Colony", "Orbital Habitat", 
        "Virtual Reality Landscape", "Parallel Universe", "Quantum Realm", "Galactic Library", 
        "Time Warp Field", "Dimensional Nexus", "Celestial Garden", "Orbiting Observatory", 
        "Interdimensional Marketplace", "Quantum Field Laboratory", "Alien Sanctuary",
        "Nebular Star Nursery", "Orion Arm Outpost", "Celestial Field Observatory", "Galactic Way Station"
      ],
      "SciFiPhenomena": [
        "Wormhole Travel", "Artificial Intelligence Uprising", "Galactic Federation", "Time Paradox", 
        "Quantum Anomalies", "Virtual Reality Worlds", "Alien Invasion", "Space-Time Continuum", 
        "Singularity Event", "Cosmic Storm", "Dimensional Rift", "Celestial Alignment", 
        "Quantum Entanglement Event", "Stellar Rebirth", "Galactic Convergence", "Time Loop Anomaly", 
        "Cosmic Mirage", "Nebula Awakening", "Void Storm",
        "Constellation Formation Event", "Supernova in Orion", "Galactic Alignment", "Cosmic Constellation Shift"
      ],
      "SciFiTechnology": [
        "Teleportation Gates", "Nano Tech", "Cybernetic Enhancements", "Fusion Reactors", 
        "Artificial Gravity", "Holographic Displays", "Laser Weapons", "Antimatter Bomb", 
        "Cloaking Device", "Brain-Computer Interface", "Quantum Encryption Device", "Stellar Engine", 
        "Dimensional Stabilizer", "Celestial Navigator", "Galactic Beacon", "Time Dilation Field", 
        "Quantum Resonator", "Galactic Translator", "Star Map Projector",
        "Stellar Constellation Analyzer", "Galactic Coordinate System", "Orion's Belt Locator", "Celestial Sphere Projector"
      ],
      "LightingAndEffects": [
        "Neon Lights", "Volumetric Lighting", "Ambient Light", "Real-Time VFX", "Digital 3D Effects", 
        "HDR Lighting", "Bioluminescent Glow", "Plasma Energy", "Strobe Effects", "Quantum Flare", 
        "Quantum Light Spectrum", "Stellar Reflections", "Galactic Core Lighting", "Void Darkness Effect", 
        "Supernova Light Echo", "Wormhole Illumination", "Dimensional Light Shift", "Celestial Glow", 
        "Stellar Flare Effect",
        "Constellation Glow Effect", "Starry Sky Ambient Lighting", "Galactic Core Constellation Reflection", "Pulsar Light Pattern"
      ],
      "CharacterAndDesign": [
        "Cyberpunk Character", "Stealth Warframe", "Armored Warrior", "Smooth and Detailed Face", 
        "Intricate Details", "Symmetrical Design", "Alien Life Form", "Mechanical Exoskeleton", 
        "Virtual Avatar", "Augmented Human", "Quantum Explorer", "Galactic Wanderer", "Dimensional Traveler", 
        "Celestial Guardian", "Stellar Mage", "Quantum Entity", "Galactic Diplomat", "Time Traveler", "Alien Mystic",
        "Constellation-Inspired Character", "Star Patterned Armor", "Celestial Being", "Astronomical Explorer"
      ]
    }

    negative_prompt_pool={
      "AvoidFeatures": [
        "Mouth", "Ears", "Holes", "Out of Frame", "Bad Art", "Blurry", "Bad Proportions", 
        "Gross Proportions", "Duplicate", "Bad Anatomy", "Deformed", "Ugly", "Long Neck", 
        "Cropped Head", "Cartoon", "Anime", "Overexposed", "Underexposed", "Unnatural Poses", 
        "Cluttered Composition", "Disproportionate Limbs", "Overly Symmetrical Faces", 
        "Inconsistent Shadows", "Mismatched Perspectives", "Incoherent Textures", "Floating Objects", 
        "Disconnected Elements", "Impossible Proportions", "Inconsistent Light Sources",
        "Misshapen Constellations", "Inaccurate Star Patterns", "Unrealistic Astronomical Features"
      ],
      "AvoidArtStyles": [
        "Digital Painting", "Anime Style", "Cartoon Style", "Low-Quality Artwork", "Watermarked Images", 
        "Signature", "Abstract Art", "Minimalist Art", "Impressionist Art", "Surreal Art", "Photorealistic Style", 
        "Graffiti Art", "Baroque Style", "Rococo Style", "Futurist Art", "Dada Art", "Expressionist Art", 
        "Art Nouveau Style", "Renaissance Style",
        "Non-Realistic Depictions of Space", "Overly Abstract Constellations", "Unscientific Stellar Representations"
      ],
      "AvoidScenes": [
        "Portrait of a Girl", "Face Close Up", "Pointy Ears", "Dress", "Half-Closed Eyes", "Jewelry", 
        "Sitting", "Strapless Dress", "Breasts", "Bare Shoulders", "Tiara", "Cleavage", "Long Hair", 
        "Braid", "Grey Hair", "Long Eyelashes", "Elf", "Crowded Scenes", "Busy Cityscapes", "Ordinary Daily Life", 
        "Unrelated Object Juxtaposition", "Incongruent Scene Elements", "Out-of-Place Historical Settings", 
        "Inappropriate Seasonal Settings", "Mismatched Cultural Elements", "Contradictory Architectural Styles", 
        "Inconsistent Time Periods", "Irrelevant Background Activity", "Disjointed Narrative Elements",
        "Incorrect Astronomical Positions", "Fantasy Constellations", "Unrealistic Star Formations"
      ],
      "SpecificAvoidances": [
        "Curvy", "Plump", "Fat", "Muscular Female", "3D Face", "Cropped", "Detailed Realistic Human Spaceman", 
        "Working on Mars", "Everyday Clothing", "Modern Day Technology", "Contemporary Vehicles", 
        "Realistic Animals", "Typical Office Environments", "Overly Glossy Surfaces", "Excessive Shadowing", 
        "Unrealistic Skin Tones", "Overemphasized Textures", "Anachronistic Elements", "Unrelated Genre Mixes", 
        "Clashing Color Schemes", "Incongruous Scale Differences", "Unnatural",
        "Inaccurate Star Maps", "Non-Realistic Celestial Bodies", "Fictitious Star Systems"
      ]
    }


    positive_prompt = ""
    positive_attributes = []

    # Iterate through the positive traits library
    for trait, values in positive_prompt_pool.items():
        rno1,rno2,rno3= random.sample(range(len(values)),3)
        if positive_prompt:
            positive_prompt += ", " + values[rno1] + ', ' + values[rno2] + ', ' + values[rno3] 
        else:
            positive_prompt = values[rno1] + ', ' + values[rno2] + ', ' + values[rno3] 
        positive_attributes.append({"trait_type": trait, "value": values[rno1] + ', ' + values[rno2] + ', ' + values[rno3]})
    QualityAndDetail =["Highly Detailed", "UHD Quality", "Dreamlike Art", "3D Render", 
                             "Hard Surface Modeling", "Ultra Detailed Texture", "Surreal Imagery", 
                             "High Fidelity Graphics", "Dynamic Composition", "Cinematic Style"]
    for trait in random.sample(QualityAndDetail,3):
        positive_prompt += ", " + trait
        positive_attributes.append({"trait_type": "Quality and Detail", "value": trait})
    negative_prompt = ""
    negative_attributes = []

    # Iterate through the negative traits library
    for trait, values in negative_prompt_pool.items():
        rno1,rno2,rno3 = random.sample(range(len(values)),3)
        if negative_prompt:
            negative_prompt += ", " + values[rno1] + ', ' + values[rno2] + ', ' + values[rno3] 
        else:
            negative_prompt = values[rno1] + ', ' + values[rno2] + ', ' + values[rno3] 
        negative_attributes.append({"trait_type": trait, "value": values[rno1] + ', ' + values[rno2]})

    TechnicalAvoidances = ["Worst Quality", "Low Quality", "Depth of Field Issues", 
                                "Blurriness", "Greyscale", "Monochrome", "Low Resolution", 
                                "Text in Image", "JPEG Artifacts", "Trademark", "Watermark", 
                                "Multiple Views", "Reference Sheet", "Strabismus", 
                                "Pixelation", "Color Banding", "Lens Flare", "Motion Blur"]
    for trait in TechnicalAvoidances:
        negative_prompt += ", " + trait
        negative_attributes.append({"trait_type": "Technical Avoidances", "value": trait})
    return positive_prompt, positive_attributes, negative_prompt, negative_attributes

def generateArtNFT(dataset_name = "NFT",
            POS_TEXT_PROMPT = "mountain, river, tree, cats",
            NEG_TEXT_PROMPT = 'violent',
            SPACE_UUID = "9f62111c-16aa-4111-bb24-e66b9923b0d0",
            SEED = -1,
            UI=False):
    global lagrange_api_key,private_key,wallet_address,mumbai_rpc,api_client,lag_client,chain_id,abi
    
    dot_env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    if not UI: 
      load_dotenv(dot_env_path)
      SPACE_UUID = os.environ.get("SPACE_UUID")
    
    print("Positive Prompt:", POS_TEXT_PROMPT)
    print("Negative Prompt:", NEG_TEXT_PROMPT)
    lagrange_api_key = os.getenv("LAGRANGE_API_KEY")
    private_key = os.getenv("PRIVATE_KEY") 
    wallet_address = os.getenv("WALLET_ADDRESS")

    mumbai_rpc = 'https://rpc-mumbai.maticvigil.com'
    api_client = APIClient(lagrange_api_key,private_key,mumbai_rpc,True, True)
    lag_client = LagAPI(api_client)
    chain_id = 80001
    
    # First, we need to retreive the link to the diffusion model hosted on a lagrange space through its space uuid
    # SPACE_UUID = os.environ.get("SPACE_UUID")
    if DEBUG: print("Space UUID: ",SPACE_UUID)
    print("Getting result uri from LAG")
    res = lag_client.get_result_uri_from_space_uuid(SPACE_UUID)
    if DEBUG: print(res)
    try:
        url = res['data']['job_result_uri']
    except Exception as e:
        print(str(e))
        raise Exception("Error getting url from LAG")
        
    # Then we can use the url to generate an image and upload it to the Lagrange dataset
    print("Generating image")
    image = get_image(prompt=POS_TEXT_PROMPT,negative_prompt=NEG_TEXT_PROMPT,url=url,seed=SEED)
    img_name = str(uuid.uuid4()) + ".png"
    img_path = f"{os.path.dirname(__file__)}/" + img_name
    image.save(img_path)
    if DEBUG:print(img_path)
    try:
      upload_img2lag(img_path,dataset_name,1)
      
      # Next we upload the image to IPFS, to your MCS bucket named Chainlink_NFT 
      try:
          img_link = save_to_MCS_bucket(initialize_bucket=True,overwrite_file=True,
                                    bucket_name='Chainlink_NFT',file_path=img_path,name=img_name)
      except Exception as e:
          print(str(e))
          raise Exception("Error saving image to MCS bucket") 
      # print("Image Link on MCS: ", img_link)
      
      # Now we can create an NFT
      print("Creating NFT")
      # Connecting to Mumbai Testnet
      web3 = Web3(Web3.HTTPProvider(mumbai_rpc))
      web3.middleware_onion.inject(geth_poa_middleware, layer=0)

      # check connection
      if not web3.isConnected():
          print("Failed to connect to Mumbai testnet.")
      else:
          print("Connected to Mumbai testnet.")

      # account info
      account_address = wallet_address
      private_key = private_key
      
      # construct contract instance
      contract_address = "0x5726315fcA395777423Ed13FAc6900b890666780"
      contract = web3.eth.contract(address=contract_address, abi=abi)

      # Data to be sent to the contract
      name = img_name
      description = POS_TEXT_PROMPT + '\n' + NEG_TEXT_PROMPT
      image_url = img_link
      
      # Construct transaction
      nonce = web3.eth.getTransactionCount(account_address)
      transaction = contract.functions.sendRequest(name, description, image_url).buildTransaction({
          'chainId': 80001,  # Mumbai testnet chainId is 80001
          'gas': 2000000,  # Set up appropriate gas limit
          'gasPrice': web3.toWei('50', 'gwei'),
          'nonce': nonce,
      })

      # sign transaction
      signed_tx = web3.eth.account.sign_transaction(transaction, private_key)

      # send transaction
      tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)

      # print transaction hash
      print(f"Contract Transaction hash: {web3.toHex(tx_hash)}")

      # qeury chainlink Function status
      print("Waiting for Chainlink Function to finish")
      start = time.time()
      while True:
        result = contract.functions.getResult(name).call()
        print(result)
        if result != "" and "https://" in result:
          print(result)
          break
        if result != "" and "https://" not in result:
          raise Exception("An error occured when executing the Chainlink Function")
        time.sleep(10)
        now = time.time()
        # if the time to get a metadata url is more than 2 minutes, break
        if now - start > 120:
            print("Time out")
            raise Exception("Time out when generating a metadata url")

      nonce = web3.eth.getTransactionCount(account_address)
      # mint NFT
      print("Minting NFT")
      mint = contract.functions.mint(name).buildTransaction({
        'chainId': 80001,  # Mumbai testnet chainId 是 80001
          'gas': 2000000,  # set up  appropriate 的gas limit
          'gasPrice': web3.toWei('50', 'gwei'),
          'nonce': nonce,
      })
      if DEBUG: print(mint)
      
      # sign transaction
      signed_tx = web3.eth.account.sign_transaction(mint, private_key)

      # send transaction
      tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
      mint_hash = web3.toHex(tx_hash)
      print("NFT transaction hash: ", mint_hash)
      
      os.remove(img_path)
      dataset_address = f"https://testnet.lagrangedao.org/datasets/{wallet_address}/{dataset_name}/files"
      collection_address = "https://testnets.opensea.io/collection/swan-chainlink"
      nft_contract_address = "0x046376Ae243f53612a6118993759F9BbB1Bc9257"
      
      return img_link,contract_address,nft_contract_address,dataset_address,mint_hash
    except Exception as e:
      traceback.print_exc()
      os.remove(img_path)
      raise Exception(e)
      
    
    # res = lag_client.data_nft_request(chain_id,wallet_address,dataset_name)
    # start = time.time()
    # print("Waiting for data NFT to be created")
    # while True:
    #     res = lag_client.try_claim_data_nft(wallet_address,dataset_name)
    #     if DEBUG:print(res)
    #     claimable = 'not claimable' not in res['message']
    #     res = lag_client.get_data_nft_info(wallet_address,dataset_name)
    #     if DEBUG:print(res)
    #     nft = res['data']['nft']
    #     contract_address = nft['contract_address']
        
    #     if contract_address and claimable: break
    #     if contract_address and not claimable: 
    #         print("Not claimable")
    #         break
        
    #     time.sleep(10)
    #     now = time.time()
    #     # if the time to create NFT is more than 2 minutes, break
    #     if now - start > 120:
    #         print("Time out")
    #         raise Exception("Time out")
    # if claimable: 
    #     print("Data NFT claimable")
        
    #     # print("Data NFT contract address: ",contract_address)
    
    # # Finally we create a dataset license
    # res = lag_client.create_dataset_license(wallet_address,dataset_name,contract_address,chain_id,wallet_address)
    # if res['status'] != 'success':
    #     raise Exception("Error creating dataset license")
    # print("Dataset license created")
    # # license_contract_address = res['data']['contract_address']
    # license_ipfs_uri = res['data']['ipfs_uri']
    # license_mint_hash = res['data']['mint_hash']
    # if DEBUG: print(res)
    
    # os.remove(img_path)
    # dataset_address = f"https://testnet.lagrangedao.org/datasets/{wallet_address}/{dataset_name}/files"
    
    # return img_link,contract_address,dataset_address,license_ipfs_uri,license_mint_hash
    
    
    
if __name__ == "__main__":
    # Example usage
    POS_TEXT_PROMPT, positive_attributes_list, NEG_TEXT_PROMPT, negative_attributes_list = generate_prompt()
    mcs_img_link, chainlink_function_contract_address, nft_contract_address, dataset_address, license_mint_hash  = generateArtNFT(POS_TEXT_PROMPT=POS_TEXT_PROMPT, NEG_TEXT_PROMPT=NEG_TEXT_PROMPT)
    print("MCS Image Link: ",mcs_img_link)
    print("Chainlink Function Contract address: ",chainlink_function_contract_address)
    print("NFT Contract address: ",nft_contract_address)
    print("Dataset address: ",dataset_address)
    print("Dataset license transaction hash: ","https://mumbai.polygonscan.com/tx/" + license_mint_hash)
    