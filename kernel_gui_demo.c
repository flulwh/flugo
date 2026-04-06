/*
 * kernel_gui_demo.c
 * 
 * 一个简单的内核模块，演示如何直接从内核空间操作 Framebuffer
 * 进行基本的图形绘制（画矩形和圆）。
 * 
 * 注意：这只是概念验证。现代操作系统将复杂的 GUI 逻辑保留在用户空间
 * 以保证稳定性。此代码仅用于教育目的，展示内核如何访问显存。
 * 
 * 编译方法:
 *   make
 * 加载方法 (需要 root):
 *   insmod kernel_gui_demo.ko
 * 卸载方法:
 *   rmmod kernel_gui_demo
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fb.h>
#include <linux/delay.h>
#include <linux/mm.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("AI Assistant");
MODULE_DESCRIPTION("A minimal kernel-level GUI demonstration using Framebuffer");

static struct fb_info *fbi = NULL;
static char *fb_base = NULL;

/* 简单的颜色结构 */
struct color {
    u8 red;
    u8 green;
    u8 blue;
};

/* 辅助函数：计算像素偏移并写入颜色 */
static void draw_pixel(int x, int y, struct color c) {
    if (!fbi || !fb_base) return;

    // 边界检查
    if (x >= fbi->var.xres || y >= fbi->var.yres) return;

    // 计算显存中的偏移量
    // 假设每像素 4 字节 (32bpp)，这是现代系统的标准
    // 如果是其他格式，需要根据 fbi->var.bits_per_pixel 调整
    int offset = (y * fbi->fix.line_length) + (x * 4);

    if (offset < 0 || offset >= fbi->fix.smem_len) return;

    // 写入显存 (RGB 顺序可能因硬件而异，这里假设为 RGBX 或 BGRX)
    // 大多数 PC 硬件在小端序下是 BGRA 或 RGBA，这里尝试通用写入
    fb_base[offset]     = c.blue;   // B
    fb_base[offset + 1] = c.green;  // G
    fb_base[offset + 2] = c.red;    // R
    fb_base[offset + 3] = 0xFF;     // Alpha
}

/* 绘制一个实心矩形 */
static void draw_rect(int x1, int y1, int x2, int y2, struct color c) {
    int i, j;
    for (i = y1; i <= y2; i++) {
        for (j = x1; j <= x2; j++) {
            draw_pixel(j, i, c);
        }
    }
}

/* 绘制一个简单的圆 (使用中点圆算法的简化版) */
static void draw_circle(int xc, int yc, int radius, struct color c) {
    int x = radius;
    int y = 0;
    int err = 0;

    while (x >= y) {
        draw_pixel(xc + x, yc + y, c);
        draw_pixel(xc + y, yc + x, c);
        draw_pixel(xc - y, yc + x, c);
        draw_pixel(xc - x, yc + y, c);
        draw_pixel(xc - x, yc - y, c);
        draw_pixel(xc - y, yc - x, c);
        draw_pixel(xc + y, yc - x, c);
        draw_pixel(xc + x, yc - y, c);

        y++;
        err += 1 + 2*y;
        if (2*(err-x) + 1 > 0) {
            x--;
            err += 1 - 2*x;
        }
    }
}

/* 填充屏幕背景 */
static void clear_screen(struct color c) {
    draw_rect(0, 0, fbi->var.xres - 1, fbi->var.yres - 1, c);
}

static int __init kernel_gui_init(void) {
    struct fb_var_screeninfo *var;
    
    printk(KERN_INFO "Loading Kernel GUI Demo...\n");

    // 1. 获取主要的 Framebuffer 设备 (/dev/fb0)
    fbi = registered_fb[0];
    if (!fbi) {
        printk(KERN_ERR "No framebuffer found. Is fbcon loaded?\n");
        return -ENODEV;
    }

    // 2. 映射显存到内核虚拟地址空间
    // fb_base 是显存的起始地址
    fb_base = (char *) fbi->screen_base;
    
    // 在某些架构上，screen_base 可能已经是虚拟地址，但在某些情况下可能需要 ioremap
    // 这里假设 fbi->screen_base 可直接访问 (现代 DRM/FB 通常如此)
    if (!fb_base) {
        printk(KERN_ERR "Failed to map framebuffer memory.\n");
        return -ENOMEM;
    }

    var = &fbi->var;

    printk(KERN_INFO "Framebuffer acquired: %dx%d @ %dbpp\n", 
           var->xres, var->yres, var->bits_per_pixel);
    printk(KERN_INFO "Drawing directly from Kernel Space...\n");

    // 3. 执行绘图操作
    
    // 清空屏幕为深蓝色
    clear_screen((struct color){0, 0, 50});

    // 绘制一个红色矩形 (代表窗口)
    struct color red = {200, 50, 50};
    int rect_w = var->xres / 2;
    int rect_h = var->yres / 2;
    int rect_x = (var->xres - rect_w) / 2;
    int rect_y = (var->yres - rect_h) / 2;
    
    draw_rect(rect_x, rect_y, rect_x + rect_w, rect_y + rect_h, red);

    // 绘制一个绿色圆圈 (代表按钮)
    struct color green = {50, 200, 50};
    draw_circle(var->xres / 2, var->yres / 2, rect_w / 3, green);

    // 绘制一些文字模拟 (用像素点组成简单的线条，因为内核没有字体渲染引擎)
    // 这里为了代码简洁，只画几条线表示"内核文本"
    struct color white = {255, 255, 255};
    draw_rect(rect_x + 20, rect_y + 20, rect_x + 200, rect_y + 30, white);
    draw_rect(rect_x + 20, rect_y + 40, rect_x + 150, rect_y + 50, white);

    printk(KERN_INFO "Graphics rendered successfully in kernel space!\n");
    printk(KERN_INFO "Check your screen. To remove, run 'rmmod kernel_gui_demo'.\n");

    return 0;
}

static void __exit kernel_gui_exit(void) {
    if (fbi) {
        // 清理：恢复黑色背景，避免移除模块后屏幕花掉
        clear_screen((struct color){0, 0, 0});
        printk(KERN_INFO "Kernel GUI Demo removed. Screen cleared.\n");
    }
    fbi = NULL;
    fb_base = NULL;
}

module_init(kernel_gui_init);
module_exit(kernel_gui_exit);
