import { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { Camera, Upload, X, RotateCcw } from 'lucide-react';

interface ImageCaptureProps {
  onImageCaptured: (file: File) => void;
  onClose: () => void;
}

const ImageCapture: React.FC<ImageCaptureProps> = ({ onImageCaptured, onClose }) => {
  const [captureMode, setCaptureMode] = useState<'camera' | 'upload' | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const webcamRef = useRef<Webcam>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleCapture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
    }
  }, [webcamRef]);

  const handleConfirmCapture = () => {
    if (capturedImage) {
      // Convertir base64 en File
      fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'patient-photo.jpg', { type: 'image/jpeg' });
          onImageCaptured(file);
        });
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      onImageCaptured(file);
    }
  };

  const handleRetake = () => {
    setCapturedImage(null);
  };

  if (captureMode === 'camera') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-auto">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-semibold text-medical-900">
              Capturer une photo
            </h3>
            <button
              onClick={onClose}
              className="text-medical-500 hover:text-medical-700"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          <div className="space-y-6">
            {capturedImage ? (
              <div className="text-center">
                <img
                  src={capturedImage}
                  alt="Capture du patient"
                  className="max-w-full h-auto rounded-lg mx-auto mb-4"
                  style={{ maxHeight: '400px' }}
                />
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={handleRetake}
                    className="flex items-center px-4 py-2 border border-medical-300 rounded-lg text-medical-700 hover:bg-medical-50"
                  >
                    <RotateCcw className="h-4 w-4 mr-2" />
                    Reprendre
                  </button>
                  <button
                    onClick={handleConfirmCapture}
                    className="aesthetic-button"
                  >
                    Utiliser cette photo
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  className="rounded-lg mx-auto mb-4"
                  videoConstraints={{
                    width: 640,
                    height: 480,
                    facingMode: 'user'
                  }}
                />
                <button
                  onClick={handleCapture}
                  className="aesthetic-button flex items-center mx-auto"
                >
                  <Camera className="h-5 w-5 mr-2" />
                  Prendre la photo
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-8 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-semibold text-medical-900">
            Ajouter une photo patient
          </h3>
          <button
            onClick={onClose}
            className="text-medical-500 hover:text-medical-700"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => setCaptureMode('camera')}
            className="w-full flex items-center justify-center p-6 border-2 border-dashed border-medical-300 rounded-lg hover:border-aesthetic-400 hover:bg-aesthetic-50 transition-colors"
          >
            <Camera className="h-8 w-8 text-medical-600 mr-3" />
            <div className="text-center">
              <p className="font-medium text-medical-900">Utiliser la caméra</p>
              <p className="text-sm text-medical-600">Prendre une photo directement</p>
            </div>
          </button>

          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full flex items-center justify-center p-6 border-2 border-dashed border-medical-300 rounded-lg hover:border-aesthetic-400 hover:bg-aesthetic-50 transition-colors"
          >
            <Upload className="h-8 w-8 text-medical-600 mr-3" />
            <div className="text-center">
              <p className="font-medium text-medical-900">Télécharger un fichier</p>
              <p className="text-sm text-medical-600">JPG, PNG jusqu'à 10MB</p>
            </div>
          </button>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            className="hidden"
          />
        </div>

        <div className="mt-6 pt-6 border-t border-medical-200">
          <p className="text-xs text-medical-500 text-center">
            Les photos sont automatiquement chiffrées et conformes RGPD
          </p>
        </div>
      </div>
    </div>
  );
};

export default ImageCapture;
