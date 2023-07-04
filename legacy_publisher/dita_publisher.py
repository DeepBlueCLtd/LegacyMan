
def publish_regions(map_url, regions, target_folder):
    print('outputting regions', map_url, target_folder)
    for reg in regions:
        print("outputting region", reg.shape, reg.url, reg.coords)