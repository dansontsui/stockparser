import dumpMajor_data_internet

if __name__ == '__main__':
    for j in range(1,31):
        sdate = "11003{:02d}".format(j)
        dumpMajor_data_internet.craete_history('8299',sdate)
        