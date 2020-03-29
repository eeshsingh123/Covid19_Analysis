def de_emojify(text):
    if text:
        return text.encode('ascii', 'ignore').decode('ascii')
    else:
        return ""
