import numpy as np
import sparse

from libertem.viz import visualize_simple
from .base import AnalysisResult
from .masks import BaseMasksAnalysis, SingleMaskResultSet


class PointMaskAnalysis(BaseMasksAnalysis):
    TYPE = 'UDF'

    # FIXME remove this after UDF version is final
    def get_results(self, job_results):
        shape = tuple(self.dataset.shape.nav)
        data = job_results[0].reshape(shape)
        return self.get_generic_results(data)

    def get_udf_results(self, udf_results, roi):
        data = udf_results['intensity'].data
        return self.get_generic_results(data[..., 0])

    def get_generic_results(self, data):
        if data.dtype.kind == 'c':
            return SingleMaskResultSet(
                self.get_complex_results(
                    data,
                    key_prefix='intensity',
                    title='intensity',
                    desc="intensity of the integration over the selected point",
                )
            )
        return SingleMaskResultSet([
            AnalysisResult(raw_data=data, visualized=visualize_simple(data),
                           key="intensity", title="intensity",
                           desc="intensity of the integration over the selected point"),
        ])

    def get_use_sparse(self):
        return 'sparse.pydata'

    def get_mask_factories(self):
        if self.dataset.shape.sig.dims != 2:
            raise ValueError("can only handle 2D signals currently")

        (detector_y, detector_x) = self.dataset.shape.sig

        cx = self.parameters['cx']
        cy = self.parameters['cy']

        sig_shape = self.dataset.shape.sig

        def _point_inner():
            a = sparse.COO(
                data=np.array([1]),
                coords=([int(cy)], [int(cx)]),
                shape=sig_shape
            )
            return a
        return [_point_inner]

    def get_parameters(self, parameters):
        (detector_y, detector_x) = self.dataset.shape.sig

        cx = parameters.get('cx', detector_x / 2)
        cy = parameters.get('cy', detector_y / 2)
        return {
            'cx': cx,
            'cy': cy,
            'mask_count': 1,
            'mask_dtype': np.float32,
        }
