from cv import WaveDetector, classify_arm_position


def test_classifies_raised_and_extended_arms():
    assert classify_arm_position((0, 100), (0, 50), (0, 0), 100) == "Arm raised"
    assert (
        classify_arm_position((0, 0), (50, 0), (100, 0), 100)
        == "Arm extended right"
    )
    assert (
        classify_arm_position((100, 0), (50, 0), (0, 0), 100)
        == "Arm extended left"
    )


def test_does_not_classify_a_bent_arm_as_extended():
    assert classify_arm_position((0, 0), (50, 50), (100, 0), 100) == "Arm bent"


def test_wave_detector_requires_repeated_horizontal_motion():
    detector = WaveDetector()
    assert not detector.update(0.0, 0, 0, 20)
    assert not detector.update(0.1, 30, 0, 20)
    assert not detector.update(0.2, -30, 0, 20)
    assert detector.update(0.3, 30, 0, 20)


def test_wave_detector_ignores_small_motion():
    detector = WaveDetector()
    for frame, position in enumerate((0, 5, -5, 5, -5), start=1):
        assert not detector.update(frame / 10, position, 0, 20)
