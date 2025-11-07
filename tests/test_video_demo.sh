#!/bin/bash
# Quick test of the video demo - shows the perfect path

echo "Testing Video Demo with IKEA Desk Assembly"
echo "=========================================="
echo ""
echo "This will play through the PERFECT ASSEMBLY path with videos!"
echo ""
echo "Path: Read Manual → Follow Steps → Persist → Perfect Finish"
echo ""
echo "Videos available for all steps in this path!"
echo ""

cd /Users/wangxiang/Desktop/my_workspace/memory/world_model_bench_agent

# Run the demo with automated input (perfect path)
# 1 = Select ikea_desk_partial_video_world.json
# 1 = Read manual
# 1 = Follow steps
# 1 = Persist methodically
# 1 = Perfect finish

python3 interactive_video_demo.py << EOF
1
1
1
1
1
EOF
