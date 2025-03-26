import zipfile


def zip_file_open():
    try:
        with zipfile.ZipFile("c:\\tmp\\career_1.zip", mode="r") as archive:
            print(archive.printdir())
    except zipfile.BadZipFile as error:
        print(error)



zip_file_open()