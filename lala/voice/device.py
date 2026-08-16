from typing import List, Dict, Any, Optional
from lala.utils.logging import logger

class AudioDeviceManager:
    """
    Manages discovery and selection of audio input (microphone) and output (speaker) devices.
    Applies device selection locally within LALA without modifying Windows global settings.
    """
    def __init__(self):
        self.active_input_device_id: Optional[int] = None
        self.active_output_device_id: Optional[int] = None

    def list_input_devices(self) -> List[Dict[str, Any]]:
        devices = []
        try:
            import sounddevice as sd
            hostapis = sd.query_hostapis()
            for idx, dev in enumerate(sd.query_devices()):
                if dev.get("max_input_channels", 0) > 0:
                    api_name = hostapis[dev["hostapi"]]["name"] if dev["hostapi"] < len(hostapis) else "Unknown"
                    devices.append({
                        "id": idx,
                        "name": dev.get("name", f"Mic {idx}"),
                        "channels": dev.get("max_input_channels"),
                        "sample_rate": int(dev.get("default_samplerate", 16000)),
                        "host_api": api_name,
                        "is_default": idx == sd.default.device[0]
                    })
        except Exception as e:
            logger.warning(f"Audio device discovery fallback: {e}")
            devices.append({
                "id": 0,
                "name": "Default System Microphone (Fallback)",
                "channels": 1,
                "sample_rate": 16000,
                "host_api": "MME",
                "is_default": True
            })
        return devices

    def list_output_devices(self) -> List[Dict[str, Any]]:
        devices = []
        try:
            import sounddevice as sd
            hostapis = sd.query_hostapis()
            for idx, dev in enumerate(sd.query_devices()):
                if dev.get("max_output_channels", 0) > 0:
                    api_name = hostapis[dev["hostapi"]]["name"] if dev["hostapi"] < len(hostapis) else "Unknown"
                    devices.append({
                        "id": idx,
                        "name": dev.get("name", f"Speaker {idx}"),
                        "channels": dev.get("max_output_channels"),
                        "sample_rate": int(dev.get("default_samplerate", 22050)),
                        "host_api": api_name,
                        "is_default": idx == sd.default.device[1]
                    })
        except Exception as e:
            logger.warning(f"Audio output device discovery fallback: {e}")
            devices.append({
                "id": 0,
                "name": "Default System Speaker (Fallback)",
                "channels": 2,
                "sample_rate": 22050,
                "host_api": "MME",
                "is_default": True
            })
        return devices

    def set_input_device(self, device_id: int) -> bool:
        inputs = [d["id"] for d in self.list_input_devices()]
        if device_id in inputs:
            self.active_input_device_id = device_id
            logger.info(f"Selected audio input device ID: {device_id}")
            return True
        logger.warning(f"Invalid input device ID: {device_id}")
        return False

    def set_output_device(self, device_id: int) -> bool:
        outputs = [d["id"] for d in self.list_output_devices()]
        if device_id in outputs:
            self.active_output_device_id = device_id
            logger.info(f"Selected audio output device ID: {device_id}")
            return True
        logger.warning(f"Invalid output device ID: {device_id}")
        return False
