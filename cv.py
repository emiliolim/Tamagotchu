"""Preview a camera feed and recognize basic arm positions and waving."""

from collections import deque
from math import acos, degrees, hypot
from typing import Protocol


Point = tuple[float, float]
TimedPoint = tuple[float, float]


class NormalizedLandmark(Protocol):
    x: float
    y: float


def _distance(first: Point, second: Point) -> float:
    return hypot(second[0] - first[0], second[1] - first[1])


def _elbow_angle(shoulder: Point, elbow: Point, wrist: Point) -> float:
    shoulder_vector = (shoulder[0] - elbow[0], shoulder[1] - elbow[1])
    wrist_vector = (wrist[0] - elbow[0], wrist[1] - elbow[1])
    shoulder_length = hypot(*shoulder_vector)
    wrist_length = hypot(*wrist_vector)
    if shoulder_length == 0 or wrist_length == 0:
        return 0

    cosine = sum(
        shoulder_vector[index] * wrist_vector[index] for index in range(2)
    ) / (shoulder_length * wrist_length)
    return degrees(acos(max(-1.0, min(1.0, cosine))))


def classify_arm_position(
    shoulder: Point, elbow: Point, wrist: Point, shoulder_width: float
) -> str:
    """Classify a mostly straight arm using image-space pixel coordinates."""
    if _elbow_angle(shoulder, elbow, wrist) < 145:
        return "Arm bent"

    delta_x = wrist[0] - shoulder[0]
    delta_y = wrist[1] - shoulder[1]
    arm_length = hypot(delta_x, delta_y)

    if (
        delta_y < -0.5 * arm_length
        and abs(delta_x) < 0.7 * abs(delta_y)
    ):
        return "Arm raised"

    if abs(delta_y) < 0.35 * abs(delta_x) and abs(delta_x) > 0.45 * shoulder_width:
        return "Arm extended right" if delta_x > 0 else "Arm extended left"

    return "Arm straight"


class WaveDetector:
    """Detect repeated, sufficiently large horizontal wrist reversals."""

    def __init__(self) -> None:
        self._samples: deque[TimedPoint] = deque()

    def update(
        self, timestamp: float, wrist_x: float, shoulder_x: float, min_amplitude: float
    ) -> bool:
        relative_x = wrist_x - shoulder_x
        self._samples.append((timestamp, relative_x))
        while self._samples and timestamp - self._samples[0][0] > 1.0:
            self._samples.popleft()

        if len(self._samples) < 4:
            return False

        direction = 0
        pivot = self._samples[0][1]
        reversals = 0
        for _, position in list(self._samples)[1:]:
            if direction == 0:
                if abs(position - pivot) >= min_amplitude:
                    direction = 1 if position > pivot else -1
                    pivot = position
            elif direction > 0:
                if position > pivot:
                    pivot = position
                elif pivot - position >= min_amplitude:
                    direction = -1
                    pivot = position
                    reversals += 1
            else:
                if position < pivot:
                    pivot = position
                elif position - pivot >= min_amplitude:
                    direction = 1
                    pivot = position
                    reversals += 1

        return reversals >= 2


def _pixel_point(landmark: NormalizedLandmark, width: int, height: int) -> Point:
    return (landmark.x * width, landmark.y * height)


def main(camera_index: int = 0) -> None:
    try:
        import cv2
        import mediapipe as mp

        try:
            solutions = mp.solutions
        except AttributeError:
            from mediapipe.python import solutions
    except ImportError as error:
        raise SystemExit(
            "Arm tracking requires OpenCV and MediaPipe. "
            "Install them with: python -m pip install opencv-python mediapipe==0.10.21"
        ) from error

    pose_api = solutions.pose
    drawing_utils = solutions.drawing_utils
    camera_backend = getattr(cv2, "CAP_DSHOW", cv2.CAP_ANY)
    capture = cv2.VideoCapture(camera_index, camera_backend)
    if not capture.isOpened():
        capture.release()
        capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Could not open camera {camera_index}")

    pose_landmark = pose_api.PoseLandmark
    arm_landmarks = (
        (
            "Left arm",
            pose_landmark.LEFT_SHOULDER,
            pose_landmark.LEFT_ELBOW,
            pose_landmark.LEFT_WRIST,
        ),
        (
            "Right arm",
            pose_landmark.RIGHT_SHOULDER,
            pose_landmark.RIGHT_ELBOW,
            pose_landmark.RIGHT_WRIST,
        ),
    )
    wave_detectors = {name: WaveDetector() for name, *_ in arm_landmarks}

    try:
        with pose_api.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        ) as pose:
            while True:
                success, frame = capture.read()
                if not success:
                    raise RuntimeError("The camera stopped returning frames")

                frame = cv2.flip(frame, 1)
                height, width = frame.shape[:2]
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(rgb_frame)

                if results.pose_landmarks:
                    drawing_utils.draw_landmarks(
                        frame, results.pose_landmarks, pose_api.POSE_CONNECTIONS
                    )
                    landmarks = results.pose_landmarks.landmark
                    left_shoulder = _pixel_point(
                        landmarks[pose_landmark.LEFT_SHOULDER], width, height
                    )
                    right_shoulder = _pixel_point(
                        landmarks[pose_landmark.RIGHT_SHOULDER], width, height
                    )
                    shoulder_width = max(_distance(left_shoulder, right_shoulder), 1)

                    for name, shoulder_id, elbow_id, wrist_id in arm_landmarks:
                        shoulder_landmark = landmarks[shoulder_id]
                        elbow_landmark = landmarks[elbow_id]
                        wrist_landmark = landmarks[wrist_id]
                        if min(
                            shoulder_landmark.visibility,
                            elbow_landmark.visibility,
                            wrist_landmark.visibility,
                        ) < 0.5:
                            continue

                        shoulder = _pixel_point(shoulder_landmark, width, height)
                        elbow = _pixel_point(elbow_landmark, width, height)
                        wrist = _pixel_point(wrist_landmark, width, height)
                        status = classify_arm_position(
                            shoulder, elbow, wrist, shoulder_width
                        )
                        if wave_detectors[name].update(
                            timestamp=cv2.getTickCount() / cv2.getTickFrequency(),
                            wrist_x=wrist[0],
                            shoulder_x=shoulder[0],
                            min_amplitude=shoulder_width * 0.18,
                        ):
                            status = "Waving left/right"

                        cv2.putText(
                            frame,
                            f"{name}: {status}",
                            (20, 35 + 32 * (0 if name == "Left arm" else 1)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )
                else:
                    cv2.putText(
                        frame,
                        "No person detected",
                        (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2,
                    )

                cv2.imshow("Arm tracking - press Q or Esc to quit", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
