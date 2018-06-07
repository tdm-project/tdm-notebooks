import gdal, osr
import numpy as np
import imageio
import glob
import sys

class GeoAdapter(object):
    def __init__(self, footprint):
        self.footprint = footprint
    def get_grid(self, unit='km', send_raster=False):
        raster = gdal.Open(self.footprint)
        gt = raster.GetGeoTransform()
        oX, oY, pxlW, pxlH = gt[0], gt[3], gt[1], gt[5]
        cols, rows = raster.RasterXSize, raster.RasterYSize
        factor = {'km': 0.001, 'm': 1.0}[unit]
        if send_raster:
            return oX, oY, factor * pxlW, factor * pxlH, cols, rows, raster
        else:
            return oX, oY, factor * pxlW, factor * pxlH, cols, rows
    def save_as_raster(self, data, fname):
        oX, oY, pxlW, pxlH, cols, rows, oraster = self.get_grid(unit='m', send_raster=True)
        driver = gdal.GetDriverByName('GTiff')
        raster = driver.Create(fname, cols, rows, 1, gdal.GDT_Float32)
        raster.SetGeoTransform((oX, pxlW, 0, oY, 0, pxlH))
        band = raster.GetRasterBand(1)
        band.WriteArray(data)
        rasterSRS = osr.SpatialReference()
        rasterSRS.ImportFromWkt(oraster.GetProjectionRef())
        raster.SetProjection(rasterSRS.ExportToWkt())
        band.FlushCache()        

class SignalProcessor(object):
    def __init__(self, geo_adapter):
        self.distance_field = self.compute_distance_field(geo_adapter.get_grid(unit='km'))
    def compute_distance_field(self, details):
        oX, oY, pxlW, pxlH, cols, rows = details
        x = pxlW * (np.arange(-(cols/2), (cols/2), 1) + 0.5)
        y = pxlH * (np.arange(-(rows/2), (rows/2), 1) + 0.5)
        xx, yy = np.meshgrid(x, y, sparse=True)
        return 10 * np.log(xx**2 + yy**2)
    def process(self, data):
        signal, mask = data
        #
        # rain_mat_mmh = (10**( ( (rain_mat_DN/2.55-100) + 91.4) /10) )/a_MP)**(1/b_MP)
        #Z = (0.39216 * signal - 8.6 + self.distance_field) * mask
        Z = 10**(0.1*(0.39216 * signal - 8.6))
        return (Z/300)**(1/1.5) * mask

class Aggregator(object):
    def __init__(self, path_root):
        self.path_root = path_root
    def aggregate(self, day, hour):
        return glob.glob('%s/%s_%s:*.png' % (self.path_root, day, hour))
    
class RainFallEstimator(object):
    def __init__(self, processor, aggregator):
        self.processor = processor
        self.aggregator = aggregator
    def get_image_data(self, path):
        im = imageio.imread(path)
        return im[:,:,0], im[:,:,3] == 255 # NOTE the mask is on channel 3!!!
    def get_precipitation(self, path):
        return self.processor.process(self.get_image_data(path))
    def aggregate(self, day, hour):
        paths = self.aggregator.aggregate(day, hour)
        if len(paths) > 0:
            precs = np.dstack([self.get_precipitation(x) for x in paths])
            return np.average(precs, axis=2)
        else:
            return None

def main(argv):
    footprint = argv[0]
    root_path = argv[1]
    day = argv[2]
    ga = GeoAdapter('data/radarsample/radarfootprint.tif')    
    processor = SignalProcessor(ga)
    aggregator = Aggregator(root_path)
    rfe = RainFallEstimator(processor, aggregator)
    for hour in range(24):
        rain = rfe.aggregate(day, hour)
        if rain is not None:
            fname = "%s_%s.3003.tif" % (day, hour)
            ga.save_as_raster(rain, fname)
            print('Saved %s' % fname)

if __name__ == "__main__":
    main(sys.argv[1:])
