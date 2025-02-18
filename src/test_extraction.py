import argparse
import os
import pytest
from run_extraction import main as run_extraction_main

@pytest.mark.parametrize(
    "input_args, expected_output",
    [
        (
            {
                "image_path": "input/sample_biphasic.png",
                "target_color": "#034730",
                "delta": 20,
                "kernel_size": 1,
                "thin": 6,
                "debug": False,
            },
            {
                "origin": (129, 736),         # Expected lower-left point in image coordinates
                "xlim": [0, 10],            # Expected x-axis limits
                "ylim": [-300, 300],           # Expected y-axis limits
                "median_rcs": -3,          # Expected median RCS
            }
        ),
        (
            {
                "image_path": "input/sample_noisy_sine_color.png",
                "target_color": "blue",
                "delta": 20,
                "kernel_size": 1,
                "thin": 2,
                "debug": False,
            },
            {
                "origin": (239, 1439),         # Expected lower-left point in image coordinates
                "xlim": [0, 180],            # Expected x-axis limits
                "ylim": [-30, 30],           # Expected y-axis limits
                "median_rcs": -10,          # Expected median RCS
            }
        ),
        (
            {
                "image_path": "input/sample_sine_wave.png",
                "target_color": "#1F77B4",
                "delta": 20,
                "kernel_size": 1,
                "thin": 2,
                "debug": False,
            },
            {
                "origin": (80, 427),         # Expected lower-left point in image coordinates
                "xlim": [0, 2],            # Expected x-axis limits
                "ylim": [0, 2],           # Expected y-axis limits
                "median_rcs": 1,          # Expected median RCS
            }
        ),
        (
            {
                "image_path": "input/sample_stock.png",
                "target_color": "#1F77B4",
                "delta": 20,
                "kernel_size": 1,
                "thin": 2,
                "debug": False,
            },
            {
                "origin": (80, 427),         # Expected lower-left point in image coordinates
                "xlim": [2000, 3000],            # Expected x-axis limits
                "ylim": [1100, 1600],           # Expected y-axis limits
                "median_rcs": 1300,          # Expected median RCS
            }
        ),
        (
            {
                "image_path": "input/sample_rcs.png",
                "target_color": "blue",
                "delta": 20,
                "kernel_size": 1,
                "thin": 2,
                "debug": False,
            },
            {
                "origin": (62, 365),         # Expected lower-left point in image coordinates
                "xlim": [0, 180],            # Expected x-axis limits
                "ylim": [0, 30],           # Expected y-axis limits
                "median_rcs": 8,          # Expected median RCS
            }
        ),
        (
            {
                "image_path": "input/sample_biphasic2.png",
                "target_color": "grey",
                "delta": 20,
                "kernel_size": 1,
                "thin": 6,
                "debug": True,
            },
            {
                "origin": (377, 1430),         # Expected lower-left point in image coordinates
                "xlim": [0, 10],            # Expected x-axis limits
                "ylim": [-300, 300],           # Expected y-axis limits
                "median_rcs": -3,          # Expected median RCS
            }
        ),
    ],
)
def test_run_extraction(input_args, expected_output):
    # Convert structured input_args dict to an argparse.Namespace
    args = argparse.Namespace(**input_args)
    args.output = "output/figures"
    result = run_extraction_main(args)
    
    # Check that result is a dict with required keys.
    for key in ["origin", "xlim", "ylim", "median_rcs", "data_points"]:
        assert key in result, f"Missing key: {key}"

    # Retrieve values from the result
    origin      = result["origin"]
    xlim        = result["xlim"]
    ylim        = result["ylim"]
    median_rcs  = result["median_rcs"]
    data_points = result["data_points"]

    # Compare results to expected output
    # Compare origin with tolerance by checking each coordinate.  Allow a 5px margin of error
    for res_val, expected_val in zip(origin, expected_output["origin"]):
        assert res_val == pytest.approx(expected_val, abs=5), f"Expected origin coordinate approx {expected_val}, got {res_val}"

    # assert origin == expected_output["origin"], f"Expected origin {expected_output['origin']}, got {origin}"
    assert xlim == expected_output["xlim"], f"Expected xlim {expected_output['xlim']}, got {xlim}"
    assert ylim == expected_output["ylim"], f"Expected ylim {expected_output['ylim']}, got {ylim}"
    
    # if median_rcs is not None:
    #     assert median_rcs == pytest.approx(expected_output["median_rcs"], rel=0.1), \
    #         f"Expected median_rcs approx {expected_output['median_rcs']}, got {median_rcs}"
    if median_rcs is not None:
      if expected_output["median_rcs"] == 0:
          tol = 0.1  # set an appropriate absolute tolerance for zero
          assert median_rcs == pytest.approx(expected_output["median_rcs"], abs=tol), \
              f"Expected median_rcs approx {expected_output['median_rcs']} within ±{tol}, got {median_rcs}"
      else:
          assert median_rcs == pytest.approx(expected_output["median_rcs"], rel=0.1), \
              f"Expected median_rcs approx {expected_output['median_rcs']}, got {median_rcs}"


    assert len(data_points) > 1, \
        f"Expected at least 2 data points, got {len(data_points)}"

if __name__ == "__main__":
    pytest.main([os.path.basename(__file__)])