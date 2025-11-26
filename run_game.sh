#!/bin/bash
# Quick launcher for the World Explorer Game

source venv/bin/activate

echo "🎮 World Explorer Game Launcher"
echo "================================"
echo ""
echo "Available worlds:"
echo "1. Indoor Plant (Video) - Full video transitions"
echo "2. Indoor Plant (Image) - Image-based states"
echo "3. Indoor Plant (Text) - Text-only narrative"
echo ""
read -p "Select world (1-3): " choice

case $choice in
    1)
        echo "Launching Indoor Plant Video World..."
        python game.py --video worlds/video_worlds/indoor_plant_watering_repotting_branching_egocentric_video_world.json
        ;;
    2)
        echo "Launching Indoor Plant Image World..."
        python game.py --image worlds/image_worlds/indoor_plant_watering_repotting_branching_egocentric_image_world.json
        ;;
    3)
        echo "Launching Indoor Plant Text World..."
        python game.py --text worlds/llm_worlds/indoor_plant_watering_repotting_branching_egocentric_world.json
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac
