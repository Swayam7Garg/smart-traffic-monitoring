# Sample Input Videos Directory

This directory should contain your test traffic video files.

## How to Get Test Videos

### Option 1: Record Your Own
- Use your phone or camera to record traffic at an intersection
- Recommended: 720p or 1080p resolution
- Duration: 30 seconds to 5 minutes
- Save as .mp4, .avi, or .mov format

### Option 2: Download from YouTube
Use tools like `yt-dlp` to download traffic videos:
```bash
pip install yt-dlp
yt-dlp "https://youtube.com/watch?v=VIDEO_ID" -o traffic_video.mp4
```

Search for: "traffic intersection", "4-way traffic", "busy intersection"

### Option 3: Use Stock Footage
Download free stock videos from:
- Pexels.com (search: traffic)
- Pixabay.com (search: traffic intersection)
- Videvo.net

## Recommended Video Characteristics

- **Resolution**: Minimum 720p (1280x720)
- **Frame Rate**: 24-30 fps
- **View**: Overhead or elevated angle of intersection
- **Visibility**: Clear view of all lanes
- **Duration**: 1-10 minutes
- **Format**: MP4 (H.264) preferred

## Example Usage

After adding videos to this directory:

```bash
# Run with specific video
python main.py --source data/input_videos/traffic.mp4

# Run with different video
python main.py --source data/input_videos/intersection.mp4
```

## Sample Video Names
- `traffic_4way.mp4` - Four-way intersection
- `highway_traffic.mp4` - Highway traffic
- `busy_intersection.mp4` - Busy city intersection
- `test_video.mp4` - General test video
