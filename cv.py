"""Preview a camera feed and estimate hand pose and extended fingers."""

from collections.abc import Sequence


Landmark = tuple[float, float]


def count_extended_fingers(landmarks: Sequence[Landmark], handedness: str) -> int:
    """Estimate the number of raised fingers for an upright hand."""
    if len(landmarks) != 21:
        raise ValueError("A hand must have exactly 21 landmarks")

    count = sum(
        landmarks[tip][1] < landmarks[pip][1]
        for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18))
    )

    thumb_tip_x = landmarks[4][0]
    thumb_ip_x = landmarks[3][0]
    if (handedness == "Right" and thumb_tip_x < thumb_ip_x) or (
        handedness == "Left" and thumb_tip_x > thumb_ip_x
    ):
        count += 1

    return count


def main(camera_index: int = 0) -> None:
    try:
        import cv2
        import mediapipe as mp

        if not hasattr(mp, "solutions"):
            try:
                from mediapipe.python import solutions as mp_solutions
            except ImportError as error:
                raise SystemExit(
                    "MediaPipe is installed, but the legacy hand-tracking API is missing. "
                    "Reinstall it with: python -m pip install mediapipe==0.10.21"
                ) from error
            mp.solutions = mp_solutions
    except ImportError as error:
        raise SystemExit(
            "Camera hand tracking requires OpenCV and MediaPipe. "
            "Install MediaPipe with: "
            "python -m pip install mediapipe==0.10.21"
        ) from error

    hands_api = mp.solutions.hands
    capture = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    if not capture.isOpened():
        capture.release()
        capture = cv2.VideoCapture(camera_index)
    if not capture.isOpened():
        capture.release()
        raise RuntimeError(f"Could not open camera {camera_index}")

    try:
        with hands_api.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        ) as hands:
            while True:
                success, frame = capture.read()
                if not success:
                    raise RuntimeError("The camera stopped returning frames")

                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                height, width = frame.shape[:2]

                if results.multi_hand_landmarks:
                    handedness_results = results.multi_handedness or []
                    for index, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame, hand_landmarks, hands_api.HAND_CONNECTIONS
                        )

                        handedness = "Unknown"
                        if index < len(handedness_results):
                            handedness = handedness_results[index].classification[0].label

                        normalized_landmarks = [
                            (landmark.x, landmark.y)
                            for landmark in hand_landmarks.landmark
                        ]
                        fingers = count_extended_fingers(
                            normalized_landmarks, handedness
                        )
                        wrist = hand_landmarks.landmark[0]
                        position = (int(wrist.x * width), int(wrist.y * height) - 12)
                        cv2.putText(
                            frame,
                            f"{handedness}: {fingers} fingers",
                            position,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )
                else:
                    cv2.putText(
                        frame,
                        "No hands detected",
                        (20, 35),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2,
                    )

                cv2.imshow("Hand pose - press Q or Esc to quit", frame)
                key = cv2.waitKey(1) & 0xFF
                if key in (ord("q"), 27):
                    break
    finally:
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()