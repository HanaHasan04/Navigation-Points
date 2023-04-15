# Navigation Points  

Python Implementation of Navigation Point Detection in Point Clouds for Drone Navigation.  

## Setup  
**input:** set of points P  
**output:** navigation points (interesting points – exit from room, or points that if we reached them we probably discover “new” areas)  


## Open Space Example  
<img src="https://user-images.githubusercontent.com/100927079/232217316-0d380c7b-f382-4570-9c9d-96a8ef0c2e27.png" width="50%">  
<img src="https://user-images.githubusercontent.com/100927079/232217325-8c649fa2-fa66-4f44-b851-4e0a9db62825.png" width="50%">  
<img src="https://user-images.githubusercontent.com/100927079/232217323-0b1a7b31-47c0-4a37-b4c9-82b4d06f1c3a.png" width="50%">  
<img src="https://user-images.githubusercontent.com/100927079/232217320-09c75a23-9a6c-48fd-bbac-af89a27004ee.png" width="50%">  

## Indoor Example  
<img src="https://user-images.githubusercontent.com/100927079/232222184-945fbf44-2497-493a-8bc3-f06de04c3299.png" width="50%">  
<img src="https://user-images.githubusercontent.com/100927079/232222214-06699a96-5d37-4a54-b117-b0bb95dc31ac.png" width="50%">  
<img src="https://user-images.githubusercontent.com/100927079/232222236-bea04c29-9e34-4d42-8c89-26bc7868fbec.png" width="50%">  
<img src="https://user-images.githubusercontent.com/100927079/232222412-d0fad137-b284-4064-9a40-233146782176.png" width="50%">

  
  
## Requirements  
- numpy  
- matplotlib
- sklearn  
- shapely
- statistics  
- math  
  
## Usage  
Run `scan_floor.py` as the main file to execute the project.  
 
## Acknowledgements  
The core idea of the original algorithm for finding navigation points was developed by *Livne Benhemo*.
