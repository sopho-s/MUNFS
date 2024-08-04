def StripFilenames(filename):
    filename = filename.split("/")
    if len(filename) == 0:
        if filename[0] == "":
            return "/"
        else:
            return filename[0]
    if len(filename) > 1:
        if filename[0] == "":
            return "/".join(filename[1:])
    if filename[-1] == "":
        return "/".join(filename[:len(filename)-1])
    else:
        return "/".join(filename)