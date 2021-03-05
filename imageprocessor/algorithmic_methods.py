import tempfile


def add_to_last_line_or_new_line(lines, w):
    if len(lines) > 0:
        l_word = lines[-1][-1]
        if are_words_in_acceptable_offset_distance(l_word, w):
            lines[-1].append(w)
        else:
            lines.append([w])
    else:
        lines.append([w])


def get_normalized_sequential_data_blocks(df):
    """ Converts ImageProcessor.dataFrame into a list -- unsure why it gives it a certain shape.
    StartX and start_y refer to attempting to detect a label. These are both 0 if a label ('tag') image is used. """
    d = []
    for index, w in df.iterrows():
        if w['index'] > 0:
            d.append(w)
    lines = []
    for w in d:
        add_to_last_line_or_new_line(lines, w)
    blocks = []

    def sort_key(w):
        return int(w['sp'][0])

    for line in lines:
        blocks.append(sorted(line, key=sort_key))

    def sort_key(a_line):
        return int(a_line[0]['sp'][1])

    return sorted(blocks, key=sort_key)


def meet_horizontal_alignment(x, y, max_gap=70):
    if y['sp'][0] < x['sp'][0]:
        temp_to_swap = x
        x = y
        y = temp_to_swap
    l1 = x['ep'][0] - x['sp'][0]
    l2 = y['ep'][0] - y['sp'][0]
    tl = y['ep'][0] - x['sp'][0]
    gap = y['sp'][0] - x['ep'][0]
    l_diff = abs(tl - l1 - l2 - gap)

    return l_diff == 0 and gap <= max_gap


def are_words_in_acceptable_offset_distance(w1, w2):
    horiz_alignment = meet_horizontal_alignment(w1, w2)
    vertical_offset = 15
    vert_alignment = abs(w2['sp'][1] - w1['ep'][1]) <= vertical_offset
    return horiz_alignment and vert_alignment


def get_temp_file_path(ending):
    tf = tempfile.NamedTemporaryFile()
    return tf.name + ending
    pass
