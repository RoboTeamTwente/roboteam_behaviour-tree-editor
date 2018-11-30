#!/bin/bash

cd ../../..
echo "#!/bin/bash" >> b3e.sh
echo "sudo python workspace/src/roboteam_behaviour-tree-editor/main.py" >> b3e.sh
sudo chmod 755 b3e.sh



