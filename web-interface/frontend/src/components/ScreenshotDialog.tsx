import { useState, useEffect } from 'react';
import { apiClient } from '../services/api';

interface Screenshot {
  filename: string;
  url: string;
  size: number;
}

interface ScreenshotDialogProps {
  scenarioName: string;
  onClose: () => void;
}

export function ScreenshotDialog({ scenarioName, onClose }: ScreenshotDialogProps) {
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [currentImageIndex, setCurrentImageIndex] = useState<number>(-1);

  useEffect(() => {
    loadScreenshots();
  }, [scenarioName]);

  const loadScreenshots = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.getScenarioScreenshots(scenarioName);
      // Convert relative URLs to absolute URLs pointing to backend
      const screenshotsWithAbsoluteUrls = response.screenshots.map(screenshot => ({
        ...screenshot,
        url: apiClient.getScenarioScreenshotUrl(scenarioName, screenshot.filename)
      }));
      setScreenshots(screenshotsWithAbsoluteUrls);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load screenshots');
    } finally {
      setLoading(false);
    }
  };

  const handleThumbnailClick = (screenshot: Screenshot, index: number) => {
    setSelectedImage(screenshot.url);
    setCurrentImageIndex(index);
  };

  const closeLightbox = () => {
    setSelectedImage(null);
    setCurrentImageIndex(-1);
  };

  const goToPrevious = () => {
    if (currentImageIndex > 0) {
      const newIndex = currentImageIndex - 1;
      setCurrentImageIndex(newIndex);
      setSelectedImage(screenshots[newIndex].url);
    }
  };

  const goToNext = () => {
    if (currentImageIndex < screenshots.length - 1) {
      const newIndex = currentImageIndex + 1;
      setCurrentImageIndex(newIndex);
      setSelectedImage(screenshots[newIndex].url);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!selectedImage) return;

      if (e.key === 'ArrowLeft') {
        goToPrevious();
      } else if (e.key === 'ArrowRight') {
        goToNext();
      } else if (e.key === 'Escape') {
        closeLightbox();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedImage, currentImageIndex, screenshots]);

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleLightboxBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      closeLightbox();
    }
  };

  return (
    <>
      {/* Main Dialog */}
      <div
        className="fixed inset-0 bg-slate-900 bg-opacity-40 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        onClick={handleBackdropClick}
      >
        <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[85vh] overflow-hidden flex flex-col">
          {/* Dialog Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b bg-gradient-to-r from-purple-50 to-indigo-50">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg shadow-sm">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-slate-800">Screenshots</h3>
                <p className="text-sm text-slate-600">{scenarioName}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
              title="Close"
            >
              <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Dialog Content */}
          <div className="flex-1 overflow-auto p-6">
            {loading ? (
              <div className="flex items-center justify-center h-full min-h-[300px]">
                <div className="w-10 h-10 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : error ? (
              <div className="flex items-center justify-center h-full min-h-[300px]">
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 shadow-sm">
                  {error}
                </div>
              </div>
            ) : screenshots.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full min-h-[300px] text-center">
                <svg className="w-16 h-16 text-slate-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-sm font-semibold text-slate-700 mb-2">No screenshots available</p>
                <p className="text-xs text-slate-500">
                  This scenario was recorded without screenshots enabled.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {screenshots.map((screenshot, index) => (
                  <div
                    key={screenshot.filename}
                    className="group relative aspect-square bg-gradient-to-br from-slate-50 to-slate-100 rounded-lg overflow-hidden border-2 border-slate-200 hover:border-purple-400 transition-all cursor-pointer shadow-sm hover:shadow-lg"
                    onClick={() => handleThumbnailClick(screenshot, index)}
                  >
                    <img
                      src={screenshot.url}
                      alt={screenshot.filename}
                      className="w-full h-full object-contain bg-white transition-transform group-hover:scale-105"
                      loading="lazy"
                      onError={(e) => {
                        console.error(`Failed to load image: ${screenshot.url}`);
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                    {/* Overlay on hover */}
                    <div className="absolute inset-0 bg-gradient-to-t from-purple-900/20 to-transparent opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center">
                      <div className="bg-white/90 backdrop-blur-sm rounded-full p-3 shadow-lg">
                        <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                        </svg>
                      </div>
                    </div>
                    {/* Filename label */}
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-slate-900/80 via-slate-900/40 to-transparent p-3 pt-8">
                      <p className="text-xs text-white font-mono truncate drop-shadow-lg">{screenshot.filename}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Dialog Footer */}
          {!loading && !error && screenshots.length > 0 && (
            <div className="px-6 py-3 border-t bg-slate-50 text-center">
              <p className="text-sm text-slate-600">
                {screenshots.length} screenshot{screenshots.length !== 1 ? 's' : ''} • Click to view full size
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Lightbox for full-size image */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-slate-900/95 backdrop-blur-md flex items-center justify-center z-[60] p-8"
          onClick={handleLightboxBackdropClick}
        >
          {/* Close button */}
          <button
            onClick={closeLightbox}
            className="absolute top-4 right-4 p-3 bg-white/90 hover:bg-white rounded-lg transition-all shadow-xl hover:shadow-2xl z-10"
            title="Close preview (Esc)"
          >
            <svg className="w-6 h-6 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>

          {/* Previous button */}
          {currentImageIndex > 0 && (
            <button
              onClick={(e) => { e.stopPropagation(); goToPrevious(); }}
              className="absolute left-4 top-1/2 -translate-y-1/2 p-3 bg-white/90 hover:bg-white rounded-lg transition-all shadow-xl hover:shadow-2xl z-10"
              title="Previous (←)"
            >
              <svg className="w-6 h-6 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
          )}

          {/* Next button */}
          {currentImageIndex < screenshots.length - 1 && (
            <button
              onClick={(e) => { e.stopPropagation(); goToNext(); }}
              className="absolute right-4 top-1/2 -translate-y-1/2 p-3 bg-white/90 hover:bg-white rounded-lg transition-all shadow-xl hover:shadow-2xl z-10"
              title="Next (→)"
            >
              <svg className="w-6 h-6 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}

          {/* Image container */}
          <div className="relative max-w-[85vw] max-h-[85vh] flex flex-col items-center justify-center">
            <img
              src={selectedImage}
              alt="Full size screenshot"
              className="max-w-full max-h-[85vh] w-auto h-auto object-contain rounded-lg shadow-2xl bg-white"
              onClick={(e) => e.stopPropagation()}
            />
            {/* Image counter */}
            <div className="mt-4 px-4 py-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-xl">
              <p className="text-sm font-medium text-slate-700">
                {currentImageIndex + 1} / {screenshots.length}
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
