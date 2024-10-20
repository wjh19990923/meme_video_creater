from moviepy.editor import *
import os

# 设置文件夹路径
image_folder = "memes"  # 图片文件夹路径
image_files = sorted([os.path.join(image_folder, img) for img in os.listdir(image_folder) if
                      img.endswith(".jpg") or img.endswith(".png")])

# 加载背景音乐
audio = AudioFileClip("seve_phi.m4a")
music_duration = audio.duration

# 计算每张图片的显示时长，使其均匀分配到整个音乐时间
image_duration = music_duration / len(image_files)

# 加载背景图，并获取其宽高比
background = ImageClip("background.jpg")
background_width, background_height = background.size


# 加载并居中 meme 图片，保持纵横比，并根据背景图比例调整
def resize_and_center_image(image_clip):
    image_ratio = image_clip.size[0] / image_clip.size[1]
    background_ratio = background_width / background_height

    # 如果 meme 图片的宽高比大于背景的宽高比，根据背景的宽度缩放
    if image_ratio > background_ratio:
        return image_clip.resize(width=background_width).set_position("center")
    else:
        # 否则，根据背景的高度缩放，并保持居中
        return image_clip.resize(height=background_height * 0.8).set_position("center")


# 对所有 meme 图片进行缩放和居中处理
image_clips = [
    resize_and_center_image(ImageClip(m).set_duration(image_duration))
    for m in image_files
]

# 合成为视频，添加背景音乐并应用淡出效果（最后3秒音量降到0）
video = concatenate_videoclips(image_clips, method="compose").set_audio(audio.audio_fadeout(3))

# 设置背景图时长，并合成最终视频
background = background.set_duration(video.duration)
final_video = CompositeVideoClip([background, video])


# 添加进度条 (淡黄色方块)
def make_progress_bar(t):
    duration = video.duration
    bar_width = max(1, int(background_width * t / duration))  # 进度条的宽度随时间变化
    bar_height = 20  # 固定进度条高度
    # 使用淡黄色作为进度条的颜色
    bar = ColorClip(size=(bar_width, bar_height), color=(255, 255, 102))  # 淡黄色进度条
    return bar.set_position((0, background_height - bar_height)).get_frame(t)  # 固定在底部


# 使用 VideoClip 生成进度条图像帧
progress_bar = VideoClip(make_progress_bar, duration=video.duration)

# 合成最终视频，将进度条添加到视频底部
final_video = CompositeVideoClip([final_video, progress_bar])

# 输出视频，设置多线程提升速度
final_video.write_videofile("output_video.mp4", fps=1, threads=8)
