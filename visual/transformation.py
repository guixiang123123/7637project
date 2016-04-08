from visual import algorithm
from PIL import Image
from PIL import ImageChops
from visual import shapes
from visual import utility
import math

def equality(source, compare):

    if round(algorithm.calc_rms(source, compare), 0) < 970.0:
        return True
    else:
        return False

def shape_match(figure):

    comparison_shapes = shapes.load_shapes()
    scores = []
    for shape in comparison_shapes:

        blobs = algorithm.get_blobs(algorithm.find_regions(figure))

        # need to get inner figure object
        scores.append((shape.name, algorithm.calc_rms(blobs[-1], shape.object)))

    m = min(scores, key=lambda t: t[1])
    return m[0]

def op_transform(im1, im2, operation):

    source, compare = utility.open_image(im1, im2)

    if operation == 'xor':
        x = algorithm.xor(source, compare)
        return x
    elif operation == 'union':
        x = ImageChops.multiply(source, compare)
        return x
    elif operation == 'subtract':
        x = algorithm.subtract(source, compare)
        return x
    elif operation == 'intersect':
        x = algorithm.intersect(source, compare)
        return x
    elif operation == 'modified-subtract-horizontal':
        x = algorithm.modified_subtract(source, compare, 'horizontal')
        return x
    elif operation == 'modified-subtract-vertical':
        x = algorithm.modified_subtract(source, compare, 'vertical')
        return x

def outer_shape(source, compare):

    source_blobs = algorithm.get_blobs(algorithm.find_regions(source))
    compare_blobs = algorithm.get_blobs(algorithm.find_regions(compare))

    if len(source_blobs) < 2 or len(compare_blobs) < 2:
        return None
    else:
        source_inner = algorithm.get_center(source_blobs)
        compare_inner = algorithm.get_center(compare_blobs)

        source_blobs.pop(source_inner)
        compare_blobs.pop(compare_inner)

        source_outer = algorithm.write_blobs(source_blobs)
        compare_outer = algorithm.write_blobs(compare_blobs)

        return equality(source_outer, compare_outer)

def inner_shape(source, compare):

    source_blobs = algorithm.get_blobs(algorithm.find_regions(source))
    compare_blobs = algorithm.get_blobs(algorithm.find_regions(compare))

    source_inner = source_blobs[algorithm.get_center(source_blobs)]
    compare_inner = compare_blobs[algorithm.get_center(compare_blobs)]

    return equality(source_inner, compare_inner)

def size_comparison(source, compare):

    source_size = algorithm.find_image_size(source)
    compare_size = algorithm.find_image_size(compare)

    if compare_size > source_size and (compare_size - source_size) > 1000:
        return 'expanded'
    elif source_size > compare_size and (source_size - compare_size) > 1000:
        return 'contracted'
    else:
        return 'unchanged'

def fill_delta(source, compare):

    source_count = algorithm.fill_ratio(source)
    compare_count = algorithm.fill_ratio(compare)

    if source_count < compare_count and (compare_count - source_count) > 1500:
        return 'added'
    elif source_count > compare_count and (source_count - compare_count) > 1500:
        return 'removed'
    else:
        return 'unchanged'

def shape_delta(source, compare):

    source_count = len(algorithm.find_regions(source))
    compare_count = len(algorithm.find_regions(compare))

    if source_count < compare_count:
        return 'added'  # + str(compare_count - source_count)
    elif source_count > compare_count:
        return 'removed'  # + str(source_count - compare_count)
    else:
        return 'unchanged'

def find_alignment(figure, problemType):

    if problemType == '3x3':
        image_sections = algorithm.get_sections(figure, (184, 184), 3, 3)
    else:
        image_sections = algorithm.get_sections(figure, (184, 184), 2, 2)

    pixel_ratios = []
    for i, section in enumerate(image_sections):
        pixel_ratios.append( (i, algorithm.fill_ratio(section)) )

    max_filled = max(pixel_ratios, key=lambda t: t[1])

    if max_filled[0] == 0:
        return 'left', 'top'
    elif max_filled[0] == 1:
        return 'left', 'center'
    elif max_filled[0] == 2:
        return 'left', 'bottom'

    elif max_filled[0] == 3:
        return'center', 'top'
    elif max_filled[0] == 4:
        return 'center', 'center'
    elif max_filled[0] == 5:
        return 'center', 'bottom'

    elif max_filled[0] == 6:
        return 'right', 'top'
    elif max_filled[0] == 7:
        return 'right', 'center'
    elif max_filled[0] == 8:
        return 'right', 'bottom'

def alignment(figure1, figure2, orientation, problemType):

    alignment1 = find_alignment(figure1, problemType)
    alignment2 = find_alignment(figure2, problemType)

    keyword = ['', '']
    if alignment1 == alignment2:
        return 'unchanged'
    else:
        # x direction
        if alignment1[0] == 'left':

            if alignment2[0] == 'left':
                keyword[0] = ''
            if alignment2[0] == 'center':
                keyword[0] = 'right'
            if alignment2[0] == 'right':
                keyword[0] = 'right'

        if alignment1[0] == 'center':

            if alignment2[0] == 'left':
                keyword[0] = 'left'
            if alignment2[0] == 'center':
                keyword[0] = ''
            if alignment2[0] == 'right':
                keyword[0] = 'right'

        if alignment1[0] == 'right':

            if alignment2[0] == 'left':
                keyword[0] = 'left'
            if alignment2[0] == 'center':
                keyword[0] = 'left'
            if alignment2[0] == 'right':
                keyword[0] = ''

        # y direction
        if alignment1[1] == 'top':

            if alignment2[1] == 'top':
                keyword[1] = ''
            if alignment2[1] == 'center':
                keyword[1] = 'down'
            if alignment2[1] == 'bottom':
                keyword[1] = 'down'

        if alignment1[1] == 'center':

            if alignment2[1] == 'top':
                keyword[1] = 'up'
            if alignment2[1] == 'center':
                keyword[1] = ''
            if alignment2[1] == 'bottom':
                keyword[1] = 'down'

        if alignment1[1] == 'bottom':

            if alignment2[1] == 'top':
                keyword[1] = 'up'
            if alignment2[1] == 'center':
                keyword[1] = 'up'
            if alignment2[1] == 'bottom':
                keyword[1] = ''

        if orientation == 'horizontal':
            return keyword[0]
        else:
            return keyword[1]


def reflected_within(H1, H2):

    H1__A_sections = algorithm.get_sections(H1[0], (184, 184), 1, 2)
    H1__C_sections = algorithm.get_sections(H1[1], (184, 184), 1, 2)

    H2__D_sections = algorithm.get_sections(H2[0], (184, 184), 1, 2)
    H2__F_sections = algorithm.get_sections(H2[1], (184, 184), 1, 2)

    return (algorithm.calc_rms(H1__A_sections[0].transpose(Image.FLIP_LEFT_RIGHT), H1__A_sections[1]) <= 962.0,
            algorithm.calc_rms(H1__C_sections[0].transpose(Image.FLIP_LEFT_RIGHT), H1__C_sections[1]) <= 958.0,
            algorithm.calc_rms(H2__D_sections[0].transpose(Image.FLIP_LEFT_RIGHT), H2__D_sections[1]) <= 962.0,
            algorithm.calc_rms(H2__F_sections[0].transpose(Image.FLIP_LEFT_RIGHT), H2__F_sections[1]) <= 958.0)

def reflected_within_single(H1, H2):

    H1__A_sections = algorithm.get_sections(H1, (184, 184), 1, 2)
    H1__C_sections = algorithm.get_sections(H2, (184, 184), 1, 2)

    return (algorithm.calc_rms(H1__A_sections[0].transpose(Image.FLIP_LEFT_RIGHT), H1__A_sections[1]) < 965,
            algorithm.calc_rms(H1__C_sections[0].transpose(Image.FLIP_LEFT_RIGHT), H1__C_sections[1]) < 965)
