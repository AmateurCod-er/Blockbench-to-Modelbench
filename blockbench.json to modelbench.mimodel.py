## Blockbench Version 4.12.6
## Modelbench Version 1.15

#region Preamble
## Please ensure that the texture files are in their correct location relative to either this python file
## or the blockbench file being loaded. (You will have to do this manually).

## For example, if this python file is located at "C:/Users/blockbench.json to modelbench.mimodel.py", and the
## texture file is listed as "textures/fancy" in the blockbench model, please ensure that it's located
## at "C:/Users/textures/fancy.png".

## Or, if the blockbench model being loaded is at "D:/Downloads/texturepack/FancySword.json", and the texture
## file is still listed as "textures/fancy" in the blockbench model, please ensure that it's located at
## "D:/Downloads/texturepack/textures/fancy.png", regardless of where the python file is located.

## I don't think that blockbench supports anything other than PNGs, but this code only checks for PNGs.
## The code that loads the textures is easy to fine (Line 33 and 35) incase you don't have PNGS for some reason.
#enregion Preamble

#region User Settings
####################################################
#                  User Settings                   #
####################################################
from pathlib import Path
blockbench_path = Path(r"D:\Documents\testing.json") # Input
minemator_path = Path(r".\converted model")
## Default output writes to a folder in the same directory as the python script

#############################
# currently doesnt work lol #
#############################
favour_rotation = True
favour_position = False
## Only one of the two can be set, If both or neither are set, it defaults to 'favour_rotation'
## If you need your cubes to rotate about a specific point, use favour_rotation
## If you dont care where they rotate about, but you want to make moving them easier, use favour_position
##########################################
# set to favour rotation or things break #
# will fix later                         #
##########################################


zero_dim_spacing = 0.0005
## How far apart should the 2 faces of a cube with a dimention equal to zero, be?
## Having overlapping planes causes z-fighting, this is to compensate for that
## Both planes are moved apart by zero_dim_spacing, so the actual gap between both will be 2*zero_dim_spacing
## If you're viewing the model from close up, a smaller value is reccomended (0.0005)
## If you're viewing the model from a distance, a larger value is reccomended (0.005)

#endregion



####################################################
#                      Code                        #
####################################################
import json
from PIL import Image
import os

# Make sure both aren't set
if favour_position == favour_rotation:
    favour_rotation = True
    favour_position = False


# Load the model
with open(blockbench_path, "r") as file:
    blockbench_model = json.load(file)


# Load the textures
textures = dict()
temp = blockbench_model["textures"]
for id in temp:
    try:
        try:
            tex = Image.open(f"{temp[id]}.png")
        except:
            tex = Image.open(f"{blockbench_path.parent/temp[id]}.png")
    except:
        raise Exception(f"Texture '{temp[id]}.png' not found")
    textures[id] = tex
# Done loading textures

# Now to convert everything into planes
modelbench_model = {"name": blockbench_path.name.replace(".json", "")}
parts = []
## Oh shit, apparently you CAN use decimal values in the UV of a modelbench model.
## That is going to make this so much easier lmao.

## -Z is North, +X is East, +Z is South, -X is West 
temp = blockbench_model["elements"]
for index, bb_cube in enumerate(temp):
    mb_cube = {
        "name": None,
        "position": None,
        "rotation": None,
        "shapes": None
    }
    # Set the name of the modelbench cube
    try:
        mb_cube["name"] = bb_cube["name"]
    except:
        mb_cube["name"] = "cube"

    # Determine the position of the cube
    if favour_rotation:
        try:
            mb_cube["position"] = bb_cube["rotation"]["origin"]
        except:
            mb_cube["position"] = [0, 0, 0]
    elif favour_position:
        mb_cube["position"] = bb_cube["from"]
    else:
        raise Exception("Achivement get! How did we get here?")
        
    # Get the rotation of the cube
    if "rotation" in bb_cube and bb_cube["rotation"]["angle"] != 0:
        if bb_cube["rotation"]["axis"] == "x":
            mb_cube["rotation"] = [bb_cube["rotation"]["angle"], 0, 0]
        elif bb_cube["rotation"]["axis"] == "y":
            mb_cube["rotation"] = [0, bb_cube["rotation"]["angle"], 0]
        elif bb_cube["rotation"]["axis"] == "z":
            mb_cube["rotation"] = [0, 0, bb_cube["rotation"]["angle"]]
        else:
            if "name" in bb_cube:
                raise Exception(f"An unknown rotation was applied to '{bb_cube["name"]}' {index}")
            else:
                raise Exception(f"An unknown rotation was applied to 'cube' {index}")
    # Rotation done

    # Start actually making the planes
    shapes = []
    bb_cube["size"] = [
        bb_cube["to"][0] - bb_cube["from"][0],
        bb_cube["to"][1] - bb_cube["from"][1],
        bb_cube["to"][2] - bb_cube["from"][2]
    ]

    for direction in ["north", "east", "south", "west", "up", "down"]:
        try:
            bb_plane = bb_cube["faces"][direction]
        except:
            continue
        texture_size = list(textures[bb_plane["texture"].replace("#", "")].size)
        
        mb_plane = {
            "type": "plane",
            "description": direction,
            "texture": bb_plane["texture"].replace("#", "")+".png",
            "texture_size": texture_size,
            "from": [0, 0, 0],
            "to":[
                (bb_plane["uv"][2] - bb_plane["uv"][0]) * texture_size[0]/16,
                (bb_plane["uv"][3] - bb_plane["uv"][1]) * texture_size[0]/16,
                0
            ],
            "uv": [
                bb_plane["uv"][0] * texture_size[0]/16,
                bb_plane["uv"][1] * texture_size[0]/16
            ],
            "position": None,
            "rotation": None,
            "scale": None,
            "texture_mirror": None
        }
        

        # Offset position to match reality
        x_off, y_off, z_off = 0, 0, 0
        if favour_rotation:
            x_off = (bb_cube["from"][0] - mb_cube["position"][0])
            y_off = (bb_cube["from"][1] - mb_cube["position"][1])
            z_off = (bb_cube["from"][2] - mb_cube["position"][2])


        # Compensate for 0-dimentions
        if bb_cube["size"][0] == 0:
            match direction:
                case "west":
                    x_off -= zero_dim_spacing
                case "east":
                    x_off += zero_dim_spacing
                case _:
                    continue
        elif bb_cube["size"][1] == 0:
            match direction:
                case "down":
                    y_off -= zero_dim_spacing
                case "up":
                    y_off += zero_dim_spacing
                case _:
                    continue
        elif bb_cube["size"][2] == 0:
            match direction:
                case "north":
                    z_off -= zero_dim_spacing
                case "south":
                    z_off += zero_dim_spacing
                case _:
                    continue
        
        ## Finished:
        ## Up, Down
        ## East, West
        ## North, 
        ## I lost any semblance of trying to make things neat once I learned you could rotate UVs in Blockbench
        ## Everything was neat before the rotation-nation attacked

        #region position
        # Move the plane into place, while also accounting for bockbench UV-rotation 
        if "rotation" not in bb_plane:
            if direction in ["south", "east"]:
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    y_off,
                    bb_cube["size"][2] + z_off
                ]
            elif direction == "up":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    bb_cube["size"][1] + y_off,
                    bb_cube["size"][2] + z_off
                ]
            else:
                mb_plane["position"] = [x_off, y_off, z_off]
        elif bb_plane["rotation"] == 90:
            if direction == "east":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    bb_cube["size"][1] + y_off,
                    bb_cube["size"][2] + z_off
                ]
            elif direction == "up":
                mb_plane["position"] = [
                    x_off,
                    bb_cube["size"][1] + y_off,
                    bb_cube["size"][2] + z_off
                ]
            elif direction in ["down", "south"]:
                mb_plane["position"] = [
                    x_off,
                    y_off,
                    bb_cube["size"][2] + z_off
                ]
            elif direction == "west":
                mb_plane["position"] = [
                    x_off,
                    bb_cube["size"][1] + y_off,
                    z_off
                ]
            elif direction == "north":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    y_off,
                    z_off
                ]
        elif bb_plane["rotation"] == 180:
            if direction in ["north", "east"]:
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    bb_cube["size"][1] + y_off,
                    z_off
                ]
            elif direction == "up":
                mb_plane["position"] = [
                    x_off,
                    bb_cube["size"][1] + y_off,
                    z_off
                ]
            elif direction in "down":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    y_off,
                    bb_cube["size"][2] + z_off
                ]
            elif direction in ["west", "south"]:
                mb_plane["position"] = [
                    x_off,
                    bb_cube["size"][1] + y_off,
                    bb_cube["size"][2] + z_off
                ]
        elif bb_plane["rotation"] == 270:
            if direction == "east":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    y_off,
                    z_off
                ]
            elif direction == "up":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    bb_cube["size"][1] + y_off,
                    z_off
                ]
            elif direction == "down":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    y_off,
                    z_off
                ]
            elif direction == "west":
                mb_plane["position"] = [
                    x_off,
                    y_off,
                    bb_cube["size"][2] + z_off
                ]
            elif direction == "north":
                mb_plane["position"] = [
                    x_off,
                    bb_cube["size"][1] + y_off,
                    z_off
                ]
            elif direction == "south":
                mb_plane["position"] = [
                    bb_cube["size"][0] + x_off,
                    bb_cube["size"][1] + y_off,
                    bb_cube["size"][2] + z_off
                ]
        #endregion
        
        #region rotate and flip
        # Flip the texture if needed
        mb_plane["texture_mirror"] = direction in ["north", "south", "up"]

        # Rotate the plane to match the cube, while also accounting for bockbench UV-rotation
        if "rotation" not in bb_plane:
            match direction:
                case "north":
                    mb_plane["rotation"] = [0, 0, 0]
                case "west":
                    mb_plane["rotation"] = [0, -90, 0]
                case "down":
                    mb_plane["rotation"] = [90, 0, 0]
                case "east":
                    mb_plane["rotation"] = [0, 90, 0]
                case "up":
                    mb_plane["rotation"] = [90, 180, 0]
                case "south":
                    mb_plane["rotation"] = [0, 180, 0]
                case _:
                    raise Exception("Achivement get! How did we get here?")
        elif bb_plane["rotation"] == 90:
            match direction:
                case "north":
                    mb_plane["rotation"] = [0, 0, 90]
                case "west":
                    mb_plane["rotation"] = [0, -90, -90]
                case "down":
                    mb_plane["rotation"] = [90, 90, 0]
                case "east":
                    mb_plane["rotation"] = [0, 90, -90]
                case "up":
                    mb_plane["rotation"] = [90, 90, 0]
                case "south":
                    mb_plane["rotation"] = [0, 180, 90]
                case _:
                    raise Exception("Achivement get! How did we get here?")
        elif bb_plane["rotation"] == 180:
            match direction:
                case "north":
                    mb_plane["rotation"] = [0, 0, 180]
                case "west":
                    mb_plane["rotation"] = [0, -90, 180]
                case "down":
                    mb_plane["rotation"] = [90, 180, 0]
                case "east":
                    mb_plane["rotation"] = [0, 90, 180]
                case "up":
                    mb_plane["rotation"] = [90, 0, 0]
                case "south":
                    mb_plane["rotation"] = [0, 180, 180]
                case _:
                    raise Exception("Achivement get! How did we get here?")
        elif bb_plane["rotation"] == 270:
            match direction:
                case "north":
                    mb_plane["rotation"] = [0, 0, -90]
                case "west":
                    mb_plane["rotation"] = [0, -90, 90]
                case "down":
                    mb_plane["rotation"] = [90, -90, 0]
                case "east":
                    mb_plane["rotation"] = [0, 90, 90]
                case "up":
                    mb_plane["rotation"] = [90, -90, 0]
                case "south":
                    mb_plane["rotation"] = [0, 180, -90]
                case _:
                    raise Exception("Achivement get! How did we get here?")
        #endregion

        #region scale
        # Scale the plane so the texture size matches the cube size, while also accounting for bockbench UV-rotation
        if "rotation" not in bb_plane:
            if direction in ["north", "south"]:
                mb_plane["scale"] = [
                    bb_cube["size"][0]/mb_plane["to"][0], # X
                    bb_cube["size"][1]/mb_plane["to"][1], # Y
                    1
                ]
            elif direction in ["west", "east"]:
                mb_plane["scale"] = [
                    bb_cube["size"][2]/mb_plane["to"][0], # Z
                    bb_cube["size"][1]/mb_plane["to"][1], # Y
                    1
                ]
            elif direction in ["down", "up"]:
                mb_plane["scale"] = [
                    bb_cube["size"][0]/mb_plane["to"][0], # X
                    bb_cube["size"][2]/mb_plane["to"][1], # Z
                    1
                ]
            else:
                raise Exception("Achivement get! How did we get here?")      
        elif bb_plane["rotation"] == 90:
            if direction in ["north", "south"]:
                mb_plane["scale"] = [
                    bb_cube["size"][1]/mb_plane["to"][0],
                    bb_cube["size"][0]/mb_plane["to"][1],
                    1
                ]
            elif direction in ["west", "east"]:
                mb_plane["scale"] = [
                    bb_cube["size"][1]/mb_plane["to"][0],
                    bb_cube["size"][2]/mb_plane["to"][1],
                    1
                ]
            elif direction in ["down", "up"]:
                mb_plane["scale"] = [
                    bb_cube["size"][2]/mb_plane["to"][0],
                    bb_cube["size"][0]/mb_plane["to"][1],
                    1
                ]
            else:
                raise Exception("Achivement get! How did we get here?") 
        elif bb_plane["rotation"] == 180:
            if direction in ["north", "south"]:
                mb_plane["scale"] = [
                    bb_cube["size"][0]/mb_plane["to"][0],
                    bb_cube["size"][1]/mb_plane["to"][1],
                    1
                ]
            elif direction in ["west", "east"]:
                mb_plane["scale"] = [
                    bb_cube["size"][2]/mb_plane["to"][0],
                    bb_cube["size"][1]/mb_plane["to"][1],
                    1
                ]
            elif direction in ["down", "up"]:
                mb_plane["scale"] = [
                    bb_cube["size"][0]/mb_plane["to"][0],
                    bb_cube["size"][2]/mb_plane["to"][1],
                    1
                ]
            else:
                raise Exception("Achivement get! How did we get here?") 
        elif bb_plane["rotation"] == 270:
            if direction in ["north", "south"]:
                mb_plane["scale"] = [
                    bb_cube["size"][1]/mb_plane["to"][0],
                    bb_cube["size"][0]/mb_plane["to"][1],
                    1
                ]
            elif direction in ["west", "east"]:
                mb_plane["scale"] = [
                    bb_cube["size"][1]/mb_plane["to"][0],
                    bb_cube["size"][2]/mb_plane["to"][1],
                    1
                ]
            elif direction in ["down", "up"]:
                mb_plane["scale"] = [
                    bb_cube["size"][2]/mb_plane["to"][0],
                    bb_cube["size"][0]/mb_plane["to"][1],
                    1
                ]
            else:
                raise Exception("Achivement get! How did we get here?") 
        #endregion

        shapes.append(mb_plane)
    
    mb_cube["shapes"] = shapes


    parts.append(mb_cube)

modelbench_model["parts"] = parts
# Converting everything in to planes done


# Save the mimodel itself (very easy)
os.makedirs(minemator_path, exist_ok=True)
with open(minemator_path/blockbench_path.name.replace(".json", ".mimodel"), "w") as file:
    json.dump(modelbench_model, file, indent=4)

# Save the images (also very easy)
for tex in textures:
    textures[tex].save(minemator_path/(tex+".png"), quality=100, optimize=True)
# Saving done



print(f"Successfully converted {blockbench_path.name} into {blockbench_path.name.replace(".json", ".mimodel")}")
