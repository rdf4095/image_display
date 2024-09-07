"""
program: image_canvas_static.py

purpose: Display up to 4 images in one canvas, with constant size.

comments: Display viewports are set to a height-width ratio of 4:3.
            image shapes are: portrait | or landscape --
            viewport display order:
            vp_0  vp_1
            vp_2  vp_3

            images can be positioned according to this logic:
            landscape first:     OR      portrait first:
            -- |                         |  --
            |  --                        -- |

author: Russell Folks

history:
-------
07-24-2024  creation
07-30-2024  Add buttons to change image placement.
08-03-2024  Combine image-move functions into one fxn.
08-06-2024  Calculate the window geometry needed after images are displayed, and
            use this to control window minimum and reset.
08-08-2024  Test canvas: actual size is slightly larger than configured size.
08-14-2024  Add function find_largest_objs to re-order the list of image paths
            according to image size.
08-21-2024  Handle list of 2 images.
08-24-2024  Set variables for displaying viewport borders. Make borders optional.
08-26-2024  Pass arguments to align_images() instead of using globals.
08-27-2024  Move layout comment to header, delete redundant variables. Move the
            calculation and display of viewport borders (layout) to new function,
            show_layout.
08-29-2024  Bug fix: correctly re-order height/width lists.
08-30-2024  More efficient way to re-order image lists, without opening files
            a second time.
09-03-2024  Test align_images and align_images_2 with a list of values slightly
            different from 'widths'. This works, but should the code prevent
            images from overflowing the viewport?
09-05-2024  Type-hint the event parameter in align_images, add comments.
            Remove the button to align images.
09-07-2024  Test canvas_ui.py/get_1_posn, to set image positions individually.
"""
"""
TODO: - Consider another arrangement option: group around canvas center.
      - If only two images, need option to dispay side-by-side or 1st-over-2nd.
      - Future: for conform_canvas_to_images(), handle images displayed 
        side-by-side (shrink to viewport height) vs 1st-above-2nd
        (shrink to viewport width.)
"""

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk
from importlib.machinery import SourceFileLoader

import canvas_ui as cnv

styles_ttk = SourceFileLoader("styles_ttk", "../styles/styles_ttk.py").load_module()
custui = SourceFileLoader("custui", "../../development/python/pandas_02/rf_custom_ui.py").load_module()

def reset_window_size(dims: str) -> None:
    root.geometry(dims)


def set_all_posn(vp, widths, heights, horiz, vert) -> None:
    print('in set_all_posn:')
    print(f'   widths: {widths}')

    # set all image positions
    # posn = cnv.get_posn(vp, widths, heights, horiz, vert)

    # test get_posn
    # print(f'{heights[0]}, {posn[0].y}')
    # print(f'{heights[1]}, {posn[1].y}')
    # print(f'{heights[2]}, {posn[2].y}')
    # print(f'{heights[3]}, {posn[3].y}')

    # with get_1_posn(), each image must be set individually.
    posn1 = cnv.get_1_posn(vp, widths[0], heights[0], horiz, vert)
    posn2 = cnv.get_1_posn(vp, widths[1], heights[1], horiz, vert, True)
    posn3 = cnv.get_1_posn(vp, widths[2], heights[2], horiz, vert, False, True)
    posn4 = cnv.get_1_posn(vp, widths[3], heights[3], horiz, vert, True, True)
    
    # test get_1_posn
    # print(f'{posn1.x}, {posn1.y}')
    # print(f'{posn2.x}, {posn2.y}')
    # print(f'{posn3.x}, {posn3.y}')
    # print(f'{posn4.x}, {posn4.y}')

    # canv_static1.moveto(1, posn[0].x, posn[0].y)
    canv_static1.moveto(1, posn1.x, posn1.y)
    canv_static1.moveto(2, posn2.x, posn2.y)
    canv_static1.moveto(3, posn3.x, posn3.y)
    canv_static1.moveto(4, posn4.x, posn4.y)


    # canv_static1.moveto(2, posn[1].x, posn[1].y)
    # if len(heights) > 2:
    #     canv_static1.moveto(3, posn[2].x, posn[2].y)
    # if len(heights) > 3:
    #     canv_static1.moveto(4, posn[3].x, posn[3].y)


def order_by_size(dims: list, paths: list) -> list:
    """Find the 2 images of greatest dimension.
    
    dims specifies the dimension, as width or height.
    This function should only be called if len(dims) > 2.
    For 1 or 2 images, there's limited choice of display arrangement.
    """
    num_items = len(dims)
    sort_w = sorted(dims)
    largest_2 = sort_w[num_items - 2:]
    newpaths = []
    
    w1 = dims.index(largest_2[0])

    # Mask the location of the first "large" image, to find the second.
    dims_mod = dims.copy()
    dims_mod[w1] = -1
    w2 = dims_mod.index(largest_2[1])

    indices_all = [*range(len(dims))]

    indices_largest = [w1, w2]

    indices_smallest = [n for n in indices_all if n not in indices_largest]

    newpaths = [paths[w1], paths[w2]]
    if num_items >= 3:
        newpaths.insert(1, paths[indices_smallest[0]])
        if num_items >= 4:
            newpaths.insert(2, paths[indices_smallest[1]])

    return newpaths


"""
align_images: callback for the Combobox in class FramedCombobox.
Notes about using type-hinting:
The parameter 'ev' is an event passed when an item in the Combobox is
selected. With a print(type(ev)) you can confirm that the type for 'ev' is
'tkinter.Event', but you can't do: align_images(ev: tkinter.Event).
Because tkinter was imported as 'tk', use: align_images(ev: tk.Event).

You could hint with a string: align_images(ev: 'tkinter.Event') which explicitly 
suggests what is expected. However, the Pylance extension (if loaded) will
complain that tkinter is an undefined variable (no runtime problem though.)

Whether hinting with the string form or the tk.Event form, the inspect module,
inspect.signature(align_images), will properly report that the expected type
for 'ev' is 'tkinter.Event' (still a string.)
"""

def align_images(ev: tk.Event, vp: dict, widths: list, heights: list) -> None:
    """Set user-selected image alignment."""
    h = horizontal_align.get()
    v = vertical_align.get()
    # test alternate list
    # widths_test = [180, 117, 170, 180]
    set_all_posn(vp, widths, heights, h, v)

"""
align_images_2: alternate form of the callback. 
Like align_images, this is a callback executed when a Combobox item is
selected in the FramedCombo object (see code below.)
This version accesses variables in the enclosing scope, rather than having
them passed in as arguments.
Setting the callb (callback function) attribute for FramedCombo is "cleaner" 
with this form, but it may not be best practice because:
  - If module variable names change, this fxn needs updating.
  - It seems to violate "explicit is better than implicit".
"""

def align_images_2(ev) -> None:
    """Set user-selected image alignment."""
    h = horizontal_align.get()
    v = vertical_align.get()
    # test alternate list
    # widths_test = [180, 117, 170, 180]
    set_all_posn(viewport1, widths, heights, h, v)

"""
Further discussion on image alignment:
You could pass a list other than 'widths' (let's say 'w2'), and the images will
be shifted left-right depending on how much the values in w2 differ from
widths. The display position is calculated in get_posn() in the canvas_ui
module, and will handle any inputs. However, it does not detect if images are
outside the viewport limits, so images might be truncated on one side, which
may or may not be what you want. The same applies to heights.

One reason for passing different widths/heights is to fine-tune the display
position. However, this isn't the best way to do that, because it is entirely
the calling routine's responsibility to set reasonable limits to prevent
ovetflow. Most routines in the current version of the app don't know the true
image size, that is, independent of 'heights' and 'widths'.
A better way to fine-tune is to introduce an argument for horizontal or
vertical offset. Since get_posn (or its caller) already has heights, widths
and vp, it would be straightforward to control overflow.
"""


def show_vp_borders(canv: object, vp: dict) -> None:
    """Display rectangles to show the viewport (vp) borders within a canvas.

    Calculation of rectangle size and location is independent of vp size,
    but as an example calculation, assume viewports 200-wide, 150-high, and
    gutter between viewports of 10.
    vp_wd   = 200
    vp_wd_z = 199 = vp_wd - 1
    vp_wdx2_z = 399 = (vp_wd * 2) - 1

    vp_ht   = 150
    vp_ht_z = 149 = vp_ht - 1
    vp_htx2 = 300 = vp_ht * 2
    """
    gutter = vp['gutter']
    width_pixel = vp['w']-1
    widthx2_pixel = (vp['w'] * 2) - 1
    height_pixel = vp['h']-1
    heightx2 = vp['h'] * 2

    # Left Upper and Right Lower coordinates
    v1_LU = 0, 0
    v1_RL = width_pixel, height_pixel

    v2_LU = vp['w'] + gutter, 0 
    v2_RL = widthx2_pixel + gutter, height_pixel

    v3_LU = 0, vp['h'] + gutter
    v3_RL = width_pixel, heightx2 + gutter

    v4_LU = vp['w'] + gutter, vp['h'] + gutter
    v4_RL = widthx2_pixel + gutter, heightx2 + gutter

    canv.create_rectangle(v1_LU + v1_RL)
    canv.create_rectangle(v2_LU + v2_RL)
    canv.create_rectangle(v3_LU + v3_RL)
    canv.create_rectangle(v4_LU + v4_RL)


# app window
default_dims = ""

root = tk.Tk()
root.resizable(1, 1)
root.title("image, ttk, pack")

style2 = styles_ttk.CreateStyles()

viewport1 = {'w': 200, 'h': 150, 'gutter': 10}
# viewport1 = {'w': 400, 'h': 300, 'gutter': 10}
my_pady = 10
show_layout = True
conform_canvas_to_images = False

canvas_reconfig = {'w': viewport1['w'] * 2 + viewport1['gutter'],
                   'h': viewport1['h'] * 2 + viewport1['gutter']}

lab = ttk.Label(root, text="up to 4 fixed-size images",
                style="MyLabel.TLabel")
lab.pack(pady=my_pady)

"""
image_paths = ['four moods_2.png',      tall
               'forest of death_1.png', tall
               'parapsycho_1.png',      wide
               'four moods_1.png',      wide
               ]
"""
image_paths = ['four moods_2.png',
               'forest of death_1.png',
               'parapsycho_1.png',
               'four moods_1.png',
               ]
# test with only 2 images
# image_paths = ['forest of death_1.png',
#                'parapsycho_1.png'
#                ]
myPhotoImages_start = []
heights_start = []
widths_start = []
myPhotoImages = []
heights = []
widths = []

for i, n in enumerate(image_paths):
    im_path = 'images/' + n
    im = Image.open(im_path)
    imsize = cnv.init_image_size(im, viewport1)
    widths_start.append(imsize['w'])
    heights_start.append(imsize['h'])

    im_resize = im.resize((imsize['w'], imsize['h']))
    im_tk = ImageTk.PhotoImage(im_resize)
    # print(f'    im_tk: ({im_tk.width()}, {im_tk.height()})')
    myPhotoImages_start.append(im_tk)

new_image_paths = order_by_size(widths_start, image_paths)

# re-order the images and their shapes
# method 1: Use new path list to get each image and reconstruct widths, heights.
# --------
# In this method, the last 3 lines would not be needed in the previous enumerate.
# for i, n in enumerate(new_image_paths):
#     im_path = 'images/' + n
#     im = Image.open(im_path)
#     imsize = cnv.init_image_size(im, viewport1)
#     heights.append(imsize['h'])
#     widths.append(imsize['w'])
#     im_resize = im.resize((imsize['w'], imsize['h']))
#     im_tk = ImageTk.PhotoImage(im_resize)
#     myPhotoImages.append(im_tk)
    
#     print(f"  im {i} ({n}), {widths[i]}, {heights[i]}")
# print()

# method 2: Use new path list to find and re-order the existing lists
# --------
#           (widths, heights, myPhotoImages.)
#           Does not require opening the images and reading sizes again.
for i, n in enumerate(new_image_paths):
    orig = image_paths.index(n)
    print(i, n, orig)
    # print(f'found {n} at {orig}')
    widths.append(widths_start[orig])
    heights.append(heights_start[orig])
    myPhotoImages.append(myPhotoImages_start[orig])

# compare method 2 to method 1
# print(f'widths: {widths}')
# print(f'widths_new: {widths_new}')
# print(f'heights: {heights}')
# print(f'heights_new: {heights_new}')

canv_static1 = tk.Canvas(root, background="green")
canv_static1.configure(width=canvas_reconfig['w'], height=canvas_reconfig['h'],
                       borderwidth=0)

posn = cnv.get_posn(viewport1, widths, heights, 'left', 'top')

imid_list = []
for i, n in enumerate(new_image_paths):
    tagname = "tag_im" + str(i)
    imid = canv_static1.create_image(posn[i].x, posn[i].y, anchor=tk.NW, image=myPhotoImages[i],
                                  tag = tagname)
    imid_list.append(imid)

canv_static1.pack(ipadx=0, ipady=0, pady=10)
canv_static1.update()

if conform_canvas_to_images:
    canv_static1.configure(width=canvas_reconfig['w'], height=viewport1['h'])

"""
Scale the canvas to hold the images with no extra space.
This is to handle future situations like:
  1) all imgs smaller than the viewport width, with no re-scaling
  2) all imgs smaller than the viewport height, with no re-scaling
  3) after re-scaling, all img widths or heights smaller than corresponding
     canvas dimension.
In all 3 cases, remove "extra" canvas width or height. The purpose is to allow
other objects to be positioned closer to the canvas.
"""
# canvas_config_ht = max(sum(heights[0::2]), sum(heights[1::2])) + viewport['gutter']
# print(f'final gutter: {viewport1["gutter"]}')
# canvas_reconfig['h'] = max(sum(heights[0::2]) + viewport1['gutter'],
#                            sum(heights[1::2]) + viewport1['gutter'])
# print(f'canvas_reconfig h: {canvas_reconfig["h"]}')
# canvas_reconfig['h'] += (viewport1['gutter'])
# print(f'canvas_reconfig h: {canvas_reconfig["h"]}')

# print()
# print(f"static canv reconfig w,h: {canvas_reconfig['w']}, {canvas_reconfig['h']}")

# canv_static1.configure(width=canvas_reconfig['w'], height=canvas_reconfig['h'])

# UI elements ----------
ui_fr = ttk.Frame(root, relief='groove')

if show_layout:
    show_vp_borders(canv_static1, viewport1)

verticals = ['top', 'center', 'bottom']
horizontals = ['left', 'center', 'right']
vertical_align = tk.StringVar()
horizontal_align = tk.StringVar()

v_choice = custui.FramedCombo(ui_fr,
                              cb_values=verticals,
                              display_name='vertical',
                              name='v_choice',
                              var=vertical_align,
                              callb=lambda ev, 
                                           vp=viewport1,
                                           ws = widths,
                                           hs = heights: align_images(ev, vp, ws, hs),
                            #   callb=align_images_2,
                              posn=[0,0])
h_choice = custui.FramedCombo(ui_fr,
                              cb_values=horizontals,
                              display_name='horizontal',
                              name='h_choice',
                              var=horizontal_align,
                              callb=lambda ev,
                                           vp=viewport1,
                                           ws = widths,
                                           hs = heights: align_images(ev, vp, ws, hs),
                            #   callb=align_images_2,
                              posn=[0,1])

but_reset_size = ttk.Button(ui_fr,
                            text="reset window size",
                            command=lambda dims=default_dims: reset_window_size(dims),
                            style="MyButton1.TButton")
but_reset_size.grid(row=2, column=0)

ui_fr.pack(side='top', ipadx=10, ipady=10, padx=5, pady=5)
ui_fr.update()

btnq = ttk.Button(ui_fr,
                  text="Quit",
                  command=root.quit,
                  style="MyButton1.TButton")
# btnq.pack(side="top", fill='x', padx=5, pady=5)
btnq.grid(row=3, column=0)

# report some layout dimensions
# ------
# print(f'canv_static1 h,w: {canv_static1.winfo_height()}, {canv_static1.winfo_width()}')
# print(f'ui_fr h,w: {ui_fr.winfo_height()}, {ui_fr.winfo_width()}')
# print(f'lab h,w: {lab.winfo_height()}, {lab.winfo_width()}')

total_ht = lab.winfo_height() + canv_static1.winfo_height() + ui_fr.winfo_height()
total_wd = max(lab.winfo_width(), canv_static1.winfo_width(), ui_fr.winfo_width())
default_dims = f'{total_wd}x{total_ht}'

# optional: report function signatures.
# import inspect

# print('align_images:')
# sig = (inspect.signature(align_images))
# print(f'   signature: {sig}')


root.minsize(total_wd, total_ht)

if __name__ == "__main__":
    root.mainloop()
