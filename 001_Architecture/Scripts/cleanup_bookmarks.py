import os
import shutil

src1 = "/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library/Bookmarks/Freepik.md"
src2 = "/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library/Bookmarks/Graphify-On-Device-Knowledge-Graph-Engine.md"
dst_dir = "/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library/Tools/"
bookmarks_dir = "/Users/tonymacbook2025/Documents/Agent-OS/007_Resource_Library/Bookmarks"

if os.path.exists(src1): shutil.move(src1, dst_dir)
if os.path.exists(src2): shutil.move(src2, dst_dir)

if os.path.exists(bookmarks_dir) and not os.listdir(bookmarks_dir):
    os.rmdir(bookmarks_dir)
    print("Successfully removed Bookmarks directory.")
