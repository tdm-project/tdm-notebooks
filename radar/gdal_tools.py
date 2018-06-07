def extract_tfw(path):
    src = gdal.Open(path)
    xform = src.GetGeoTransform()
    return xform[1], xform[2], xform[4], xform[5], xform[0]+xform[1]/2, xform[3]+xform[5]/2

def extract_prj(path):
    src = gdal.Open(path)
    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(src.GetProjection())
    src_srs.MorphToESRI()
    return src_srs.ExportToWkt()
# From https://gis.stackexchange.com/questions/139906/replicating-result-of-gdalwarp-using-gdal-python-bindings
def get_wkt(srs_code):
    # checks? we need no stinking checks!
    geo, code = srs_code.split(':')
    srs = osr.SpatialReference()
    # force geo to EPSG for the time being
    srs.ImportFromEPSG(int(code))
    return srs.ExportToWkt()

def warp(in_path, out_path, t_srs, s_srs=None):
    src_ds = gdal.Open(in_path)
    dst_wkt = get_wkt(t_srs)
    dst_srs = osr.SpatialReference()
    src_wkt = None if s_srs is None else get_wkt(s_srs)
    error_threshold = 0.125
    resampling = gdal.GRA_NearestNeighbour
    # Call AutoCreateWarpedVRT() to fetch default values for target raster dimensions and geotransform
    tmp_ds = gdal.AutoCreateWarpedVRT(src_ds,
                                      src_wkt,
                                      dst_wkt,
                                      resampling,
                                      error_threshold)
    # Create the final warped raster
    dst_ds = gdal.GetDriverByName('GTiff').CreateCopy(out_path, tmp_ds)
