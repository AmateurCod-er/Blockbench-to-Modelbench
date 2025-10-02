# Blockbenchto-Modelbench
Converts Blockbench models directly to Modelbench models on a Per-face UV basis

Currently only works with Blockbench models exported as "Block/Item Model", in which it exports to a .json file.
.bbmodels are also JSON-formatted, but currently are not supported.

Additionally, you have to manually move the textures into the right spots.

## How to use:
1. Export your blockbench model to "Block/Item Model"
2. Move all of the textures to their correct relative locations (See the comments in the .py for further information)
3. Set the Input and Output paths as you desire
4. Just press run 

## Log:
##### 2025-09-14: Uploaded it to github
##### 2025-10-02: Textures can now be loaded from the same directory as the model, textures can now be saved keeping their file name
