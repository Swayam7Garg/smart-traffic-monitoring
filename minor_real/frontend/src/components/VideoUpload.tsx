import { useState, useRef } from 'react';
import { Upload, Video, X, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import { trafficAPI } from '../lib/api';

interface UploadStatus {
  file: File | null;
  progress: number;
  status: 'idle' | 'uploading' | 'processing' | 'completed' | 'error';
  message: string;
  jobId?: string;
}

export const VideoUpload: React.FC = () => {
  const [selectedJunction, setSelectedJunction] = useState<string>('junction_01');
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>({
    file: null,
    progress: 0,
    status: 'idle',
    message: '',
  });
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const junctions = [
    { id: 'junction_01', name: 'Junction 1' },
    { id: 'junction_02', name: 'Junction 2' },
    { id: 'junction_03', name: 'Junction 3' },
    { id: 'junction_04', name: 'Junction 4' },
    { id: 'junction_05', name: 'Junction 5' },
  ];

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileSelect = (file: File) => {
    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
      setUploadStatus({
        file: null,
        progress: 0,
        status: 'error',
        message: 'Invalid file type. Please upload MP4, AVI, MOV, or MKV files.',
      });
      return;
    }

    // Validate file size (max 500MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
      setUploadStatus({
        file: null,
        progress: 0,
        status: 'error',
        message: 'File too large. Maximum size is 500MB.',
      });
      return;
    }

    setUploadStatus({
      file,
      progress: 0,
      status: 'idle',
      message: `Selected: ${file.name} (${(file.size / (1024 * 1024)).toFixed(2)} MB)`,
    });
  };

  const handleUpload = async () => {
    if (!uploadStatus.file) return;

    setUploadStatus(prev => ({
      ...prev,
      status: 'uploading',
      progress: 0,
      message: 'Uploading video...',
    }));

    const formData = new FormData();
    formData.append('file', uploadStatus.file);

    try {
      // Simulate progress for upload
      const progressInterval = setInterval(() => {
        setUploadStatus(prev => {
          if (prev.progress >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return { ...prev, progress: prev.progress + 10 };
        });
      }, 200);

      const response = await trafficAPI.uploadVideo(formData, selectedJunction);
      clearInterval(progressInterval);

      setUploadStatus(prev => ({
        ...prev,
        progress: 100,
        status: 'processing',
        message: 'Processing video with YOLOv8... This may take a few minutes.',
        jobId: response.job_id,
      }));

      // Poll for job status
      pollJobStatus(response.job_id);
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.detail 
        || error.message 
        || 'Upload failed. Please try again.';
      
      setUploadStatus(prev => ({
        ...prev,
        status: 'error',
        message: `Error: ${errorMessage}`,
      }));
    }
  };

  const pollJobStatus = async (jobId: string) => {
    const maxAttempts = 60; // 5 minutes max
    let attempts = 0;

    const poll = async () => {
      try {
        const status = await trafficAPI.getJobStatus(jobId);
        
        if (status.status === 'completed') {
          const totalVehicles = status.results?.detections?.total_vehicles || 0;
          const vehicleTypes = status.results?.detections?.vehicle_types || {};
          
          setUploadStatus(prev => ({
            ...prev,
            status: 'completed',
            message: `✅ Detection completed! Found ${totalVehicles} vehicles (Cars: ${vehicleTypes.car || 0}, Bikes: ${vehicleTypes.motorcycle || 0}, Trucks: ${vehicleTypes.truck || 0}, Autos: ${vehicleTypes['auto-rickshaw'] || 0}). Click below to download annotated video.`,
          }));
        } else if (status.status === 'failed') {
          setUploadStatus(prev => ({
            ...prev,
            status: 'error',
            message: status.error || 'Processing failed.',
          }));
        } else if (attempts < maxAttempts) {
          attempts++;
          setTimeout(poll, 5000); // Poll every 5 seconds
        } else {
          setUploadStatus(prev => ({
            ...prev,
            status: 'error',
            message: 'Processing timeout. Please try again.',
          }));
        }
      } catch (error) {
        console.error('Poll error:', error);
        setUploadStatus(prev => ({
          ...prev,
          status: 'error',
          message: 'Failed to check processing status.',
        }));
      }
    };

    poll();
  };

  const handleReset = () => {
    setUploadStatus({
      file: null,
      progress: 0,
      status: 'idle',
      message: '',
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getStatusIcon = () => {
    switch (uploadStatus.status) {
      case 'uploading':
      case 'processing':
        return <Loader className="w-5 h-5 animate-spin text-blue-400" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-400" />;
      default:
        return <Video className="w-5 h-5 text-slate-400" />;
    }
  };

  const getStatusBadge = () => {
    switch (uploadStatus.status) {
      case 'uploading':
        return <Badge variant="info">Uploading</Badge>;
      case 'processing':
        return <Badge variant="warning">Processing</Badge>;
      case 'completed':
        return <Badge variant="success">Completed</Badge>;
      case 'error':
        return <Badge variant="danger">Error</Badge>;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Upload Video for Analysis</CardTitle>
          {getStatusBadge()}
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Junction Selector */}
          <div className="space-y-2">
            <label htmlFor="junction-select" className="block text-sm font-medium text-slate-300">
              Select Junction/Location
            </label>
            <select
              id="junction-select"
              value={selectedJunction}
              onChange={(e) => setSelectedJunction(e.target.value)}
              disabled={uploadStatus.status !== 'idle'}
              className="w-full px-4 py-2 bg-slate-800 border border-slate-600 rounded-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {junctions.map((junction) => (
                <option key={junction.id} value={junction.id}>
                  {junction.name}
                </option>
              ))}
            </select>
            <p className="text-xs text-slate-400">
              Video will be processed and stored under {junctions.find(j => j.id === selectedJunction)?.name}
            </p>
          </div>

          {/* Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => uploadStatus.status === 'idle' && fileInputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
              transition-all duration-200
              ${isDragging 
                ? 'border-blue-500 bg-blue-500/10' 
                : uploadStatus.file 
                  ? 'border-green-500 bg-green-500/10'
                  : 'border-slate-600 hover:border-slate-500 hover:bg-slate-800/50'
              }
              ${uploadStatus.status !== 'idle' && 'cursor-not-allowed opacity-50'}
            `}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/avi,video/mov,video/mkv"
              onChange={(e) => e.target.files && handleFileSelect(e.target.files[0])}
              className="hidden"
              disabled={uploadStatus.status !== 'idle'}
            />
            
            <div className="flex flex-col items-center gap-4">
              <div className={`
                w-16 h-16 rounded-full flex items-center justify-center
                ${uploadStatus.file ? 'bg-green-500/20' : 'bg-blue-500/20'}
              `}>
                {uploadStatus.file ? (
                  <Video className="w-8 h-8 text-green-400" />
                ) : (
                  <Upload className="w-8 h-8 text-blue-400" />
                )}
              </div>
              
              <div>
                <p className="text-lg font-medium text-slate-200 mb-1">
                  {uploadStatus.file ? uploadStatus.file.name : 'Drop video file here'}
                </p>
                <p className="text-sm text-slate-400">
                  {uploadStatus.file 
                    ? `${(uploadStatus.file.size / (1024 * 1024)).toFixed(2)} MB`
                    : 'or click to browse (MP4, AVI, MOV, MKV - Max 500MB)'
                  }
                </p>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          {(uploadStatus.status === 'uploading' || uploadStatus.status === 'processing') && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-300 flex items-center gap-2">
                  {getStatusIcon()}
                  {uploadStatus.message}
                </span>
                <span className="text-slate-400">{uploadStatus.progress}%</span>
              </div>
              <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
                  style={{ width: `${uploadStatus.progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Status Message */}
          {uploadStatus.message && uploadStatus.status !== 'uploading' && uploadStatus.status !== 'processing' && (
            <div className={`
              flex items-center gap-3 p-4 rounded-lg
              ${uploadStatus.status === 'completed' ? 'bg-green-500/10 border border-green-500/30' : ''}
              ${uploadStatus.status === 'error' ? 'bg-red-500/10 border border-red-500/30' : ''}
              ${uploadStatus.status === 'idle' && uploadStatus.file ? 'bg-blue-500/10 border border-blue-500/30' : ''}
            `}>
              {getStatusIcon()}
              <span className="text-sm text-slate-200">{uploadStatus.message}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            {uploadStatus.status === 'idle' && uploadStatus.file && (
              <>
                <Button
                  onClick={handleUpload}
                  variant="primary"
                  className="flex-1"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Start Processing
                </Button>
                <Button
                  onClick={handleReset}
                  variant="secondary"
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
              </>
            )}
            
            {uploadStatus.status === 'completed' && (
              <>
                <Button
                  onClick={() => window.open(`http://localhost:8000/api/v1/traffic/download-processed-video/${uploadStatus.jobId}`, '_blank')}
                  variant="success"
                  className="flex-1"
                >
                  <Video className="w-4 h-4 mr-2" />
                  Download Annotated Video
                </Button>
                <Button
                  onClick={handleReset}
                  variant="primary"
                  className="flex-1"
                >
                  Upload Another Video
                </Button>
              </>
            )}
            
            {uploadStatus.status === 'error' && (
              <Button
                onClick={handleReset}
                variant="danger"
                className="w-full"
              >
                Try Again
              </Button>
            )}
          </div>

          {/* Info */}
          <div className="bg-slate-800/50 rounded-lg p-4 space-y-2">
            <p className="text-sm font-medium text-slate-300">Processing Info:</p>
            <ul className="text-xs text-slate-400 space-y-1 ml-4 list-disc">
              <li>Supported formats: MP4, AVI, MOV, MKV</li>
              <li>Maximum file size: 500MB</li>
              <li>Processing time: ~30 seconds per minute of video</li>
              <li>Detection includes: Cars, Bikes, Trucks, Auto-rickshaws, Emergency vehicles</li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

