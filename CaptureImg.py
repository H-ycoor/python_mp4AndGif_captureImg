import os
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image
from datetime import datetime
import threading

# 配置常量
DEFAULT_INTERVAL = 0.1  # 默认帧间隔(秒)
MAX_FRAMES = 30         # 最大帧数限制
SUPPORTED_VIDEOS = [("视频文件", "*.mp4 *.avi *.mov")]

class ArduinoOLEDAnimationGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Video transfer to Arduino OLED")
        self.root.geometry("650x550")
        self.root.resizable(True, True)
        
        self.video_path = tk.StringVar()
        self.output_path = tk.StringVar(value=os.path.join(os.getcwd(), "frames.h"))
        self.interval = tk.DoubleVar(value=DEFAULT_INTERVAL)
        
        self.create_widgets()
    
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Arduino OLED Animation Generator", font=("Arial", 16))
        title_label.pack(pady=10)
        
        # 视频设置框架
        video_frame = ttk.LabelFrame(main_frame, text="视频设置", padding="10")
        video_frame.pack(fill=tk.X, pady=5)
        
        # 视频文件选择
        file_frame = ttk.Frame(video_frame)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_frame, text="视频文件:", width=10).pack(side=tk.LEFT)
        ttk.Entry(file_frame, textvariable=self.video_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(file_frame, text="选择", command=self.browse_video).pack(side=tk.LEFT)
        
        # 输出路径选择
        output_frame = ttk.Frame(video_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="输出路径:", width=10).pack(side=tk.LEFT)
        ttk.Entry(output_frame, textvariable=self.output_path).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(output_frame, text="另存为", command=self.save_as).pack(side=tk.LEFT)
        
        # 帧间隔设置
        interval_frame = ttk.Frame(video_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        ttk.Label(interval_frame, text="帧间隔(s):", width=10).pack(side=tk.LEFT)
        self.interval_slider = ttk.Scale(
            interval_frame, 
            from_=0.05, to=1.0, 
            variable=self.interval, 
            orient=tk.HORIZONTAL, 
            length=400
        )
        self.interval_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(interval_frame, textvariable=self.interval, width=5).pack(side=tk.LEFT)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="进度", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            variable=self.progress_var, 
            maximum=100,
            length=600
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # 日志区域
        log_frame = ttk.Frame(progress_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        self.convert_btn = ttk.Button(button_frame, text="开始转换", command=self.start_conversion, width=15)
        self.convert_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="清空日志", command=self.clear_log, width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit, width=15).pack(side=tk.LEFT, padx=5)
    
    def browse_video(self):
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=SUPPORTED_VIDEOS
        )
        if file_path:
            self.video_path.set(file_path)
    
    def save_as(self):
        file_path = filedialog.asksaveasfilename(
            title="保存输出文件",
            defaultextension=".h",
            filetypes=[("头文件", "*.h")]
        )
        if file_path:
            self.output_path.set(file_path)
    
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def start_conversion(self):
        # 验证输入
        video_path = self.video_path.get()
        output_path = self.output_path.get()
        interval = self.interval.get()
        
        if not all([video_path, output_path]):
            messagebox.showerror("错误", "请先选择视频文件和输出路径！")
            return
        
        # 禁用按钮防止重复操作
        self.convert_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        # 启动转换线程，避免UI冻结
        thread = threading.Thread(
            target=self.process_video_thread,
            args=(video_path, output_path, interval),
            daemon=True
        )
        thread.start()
    
    def process_video_thread(self, video_path, output_path, interval):
        try:
            success, message = self.process_video(
                video_path,
                output_path,
                interval,
                self.update_progress
            )
            self.log(message)
            messagebox.showinfo("完成！" if success else "错误！", message)
        except Exception as e:
            self.log(f"错误: {str(e)}")
            messagebox.showerror("错误", f"发生错误:\n{str(e)}")
        finally:
            self.progress_var.set(0)
            self.convert_btn.config(state=tk.NORMAL)
            
    def update_progress(self, current, total, saved):
        progress = current / total * 100
        self.progress_var.set(progress)
        self.log(f"处理进度: {current}/{total}帧 (已保存{saved}帧)")
        
    def process_video(self, video_path, output_path, interval, progress_callback=None):
        """视频处理核心函数"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError("无法打开视频文件")
            
            # 获取视频信息
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_interval = max(1, int(round(fps * interval)))
            
            # 准备数据结构
            frames = []
            frame_count = 0
            saved_count = 0
            
            while saved_count < MAX_FRAMES:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # 图像处理流程
                    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    resized = pil_img.resize((128, 64), Image.LANCZOS)
                    mono = resized.convert("1")
                    
                    # 生成帧数据
                    pixels = np.array(mono)
                    hex_data = []
                    for y in range(64):
                        for x in range(0, 128, 8):
                            byte = 0
                            for bit in range(8):
                                if x+bit < 128 and pixels[y, x+bit] == 0:
                                    byte |= (1 << (7 - bit))
                            hex_data.append(f"0x{byte:02X}")
                    
                    frames.append((f"frame_{saved_count:03d}", hex_data))
                    saved_count += 1
                    
                    if progress_callback:
                        progress_callback(frame_count, total_frames, saved_count)
                
                frame_count += 1
            
            # 生成.h文件
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"// 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"// 源视频: {os.path.basename(video_path)}\n")
                f.write(f"// 总帧数: {saved_count}\n\n")
                
                f.write("#ifndef FRAMES_H\n#define FRAMES_H\n\n")
                f.write("#include <Arduino.h>\n#include <avr/pgmspace.h>\n\n")
                
                # 写入各帧数据
                for name, data in frames:
                    f.write(f"const PROGMEM uint8_t {name}[] = {{\n")
                    for i in range(0, len(data), 16):
                        f.write("    " + ", ".join(data[i:i+16]) + ",\n")
                    f.write("};\n\n")
                
                # 写入索引数组
                f.write(f"const uint8_t* const all_frames[{saved_count}] PROGMEM = {{\n")
                f.write("    " + ",\n    ".join([f[0] for f in frames]) + "\n};\n\n")
                
                f.write(f"const uint16_t FRAME_COUNT = {saved_count};\n")
                f.write("#endif\n")
            
            return True, f"成功转换{saved_count}帧 -> {output_path}"
        
        except Exception as e:
            return False, f"处理失败: {str(e)}"
        finally:
            if "cap" in locals():
                cap.release()


def main():
    root = tk.Tk()
    app = ArduinoOLEDAnimationGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
