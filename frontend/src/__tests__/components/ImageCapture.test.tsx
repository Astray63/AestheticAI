import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ImageCapture from '../../components/ImageCapture';

// Mock des APIs du navigateur
Object.defineProperty(navigator, 'mediaDevices', {
  writable: true,
  value: {
    getUserMedia: jest.fn()
  }
});

// Mock de HTMLCanvasElement
HTMLCanvasElement.prototype.getContext = jest.fn(() => ({
  drawImage: jest.fn(),
  getImageData: jest.fn(() => ({ data: new Uint8ClampedArray(4) }))
})) as any;

HTMLCanvasElement.prototype.toBlob = jest.fn((callback) => {
  callback(new Blob(['fake-image-data'], { type: 'image/jpeg' }));
});

describe('ImageCapture Component', () => {
  const mockOnImageCaptured = jest.fn();
  const mockOnClose = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders camera interface correctly', () => {
    render(<ImageCapture onImageCaptured={mockOnImageCaptured} onClose={mockOnClose} />);
    
    expect(screen.getByText(/capture d'image/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /caméra/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /télécharger/i })).toBeInTheDocument();
  });

  test('enables camera successfully', async () => {
    const mockStream = {
      getTracks: jest.fn(() => [{ stop: jest.fn() }])
    };
    (navigator.mediaDevices.getUserMedia as jest.Mock).mockResolvedValue(mockStream);
    
    const user = userEvent.setup();
    render(<ImageCapture onImageCaptured={mockOnImageCaptured} onClose={mockOnClose} />);
    
    const startCameraButton = screen.getByRole('button', { name: /caméra/i });
    await user.click(startCameraButton);
    
    await waitFor(() => {
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        video: { width: 1920, height: 1080, facingMode: 'user' }
      });
    });
  });

  test('handles camera access denied', async () => {
    (navigator.mediaDevices.getUserMedia as jest.Mock).mockRejectedValue(
      new Error('Camera access denied')
    );
    
    const user = userEvent.setup();
    render(<ImageCapture onImageCaptured={mockOnImageCaptured} onClose={mockOnClose} />);
    
    const startCameraButton = screen.getByRole('button', { name: /caméra/i });
    await user.click(startCameraButton);
    
    await waitFor(() => {
      expect(screen.getByText(/erreur d'accès à la caméra/i)).toBeInTheDocument();
    });
  });

  test('validates file upload type', async () => {
    const user = userEvent.setup();
    render(<ImageCapture onImageCaptured={mockOnImageCaptured} onClose={mockOnClose} />);
    
    // Cliquer sur télécharger pour afficher l'input file
    const uploadButton = screen.getByRole('button', { name: /télécharger/i });
    await user.click(uploadButton);
    
    const fileInput = screen.getByRole('button', { name: /choisir un fichier/i });
    const invalidFile = new File(['invalid'], 'test.txt', { type: 'text/plain' });
    
    await user.upload(fileInput, invalidFile);
    
    expect(screen.getByText(/format de fichier non supporté/i)).toBeInTheDocument();
    expect(mockOnImageCaptured).not.toHaveBeenCalled();
  });

  test('accepts valid image file upload', async () => {
    const user = userEvent.setup();
    render(<ImageCapture onImageCaptured={mockOnImageCaptured} onClose={mockOnClose} />);
    
    // Cliquer sur télécharger
    const uploadButton = screen.getByRole('button', { name: /télécharger/i });
    await user.click(uploadButton);
    
    const fileInput = screen.getByRole('button', { name: /choisir un fichier/i });
    const validFile = new File(['valid-image'], 'test.jpg', { type: 'image/jpeg' });
    
    await user.upload(fileInput, validFile);
    
    await waitFor(() => {
      expect(mockOnImageCaptured).toHaveBeenCalledWith(validFile);
    });
  });

  test('validates file size limit', async () => {
    const user = userEvent.setup();
    render(<ImageCapture onImageCaptured={mockOnImageCaptured} onClose={mockOnClose} />);
    
    const uploadButton = screen.getByRole('button', { name: /télécharger/i });
    await user.click(uploadButton);
    
    const fileInput = screen.getByRole('button', { name: /choisir un fichier/i });
    // Créer un fichier trop volumineux (> 10MB)
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' });
    
    await user.upload(fileInput, largeFile);
    
    expect(screen.getByText(/fichier trop volumineux/i)).toBeInTheDocument();
    expect(mockOnImageCaptured).not.toHaveBeenCalled();
  });

  test('calls onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    render(<ImageCapture onImageCaptured={mockOnImageCaptured} onClose={mockOnClose} />);
    
    const closeButton = screen.getByRole('button', { name: /fermer/i });
    await user.click(closeButton);
    
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });
});
