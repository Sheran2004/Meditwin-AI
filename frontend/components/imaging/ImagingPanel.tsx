"use client";

import { useRef, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { classifyChestXray, type ImagingResult } from "@/lib/api";

interface Props {
  patientId: string;
}

export function ImagingPanel({ patientId }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<ImagingResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  function handleFileChange(f: File | null) {
    setFile(f);
    setResult(null);
    setPreviewUrl(f ? URL.createObjectURL(f) : null);
  }

  function drawHeatmap(heatmap: number[][]) {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const size = heatmap.length;
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const imageData = ctx.createImageData(size, size);
    for (let y = 0; y < size; y++) {
      for (let x = 0; x < size; x++) {
        const v = heatmap[y][x]; // 0..1
        const idx = (y * size + x) * 4;
        // Red-hot colormap: low = transparent, high = red/yellow
        imageData.data[idx] = 255;
        imageData.data[idx + 1] = Math.round(255 * (1 - v));
        imageData.data[idx + 2] = 0;
        imageData.data[idx + 3] = Math.round(180 * v);
      }
    }
    ctx.putImageData(imageData, 0, 0);
  }

  async function handleClassify() {
    if (!file) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await classifyChestXray(patientId, file);
      setResult(res);
      setTimeout(() => drawHeatmap(res.heatmap), 0);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Classification failed. Is GROQ_API_KEY set in backend/.env?");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <p className="mb-1 text-sm font-medium text-gray-700 dark:text-gray-200">Chest X-ray classifier (Normal vs. Pneumonia)</p>
        <p className="mb-3 text-xs text-gray-400">Proof-of-concept model — see the warning banner below before relying on any result.</p>
        <input
          type="file"
          accept="image/jpeg,image/png"
          onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
          className="block w-full text-sm text-gray-600 file:mr-3 file:rounded-lg file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:text-sm file:font-medium file:text-brand-600 dark:text-gray-300"
        />
        <Button className="mt-3" onClick={handleClassify} isLoading={isLoading} disabled={!file}>
          Classify image
        </Button>
        {error && <p className="mt-3 text-sm text-red-600 dark:text-red-400">{error}</p>}
      </Card>

      {previewUrl && (
        <Card>
          <p className="mb-3 text-sm font-medium text-gray-700 dark:text-gray-200">Image + Grad-CAM attention map</p>
          <div className="relative inline-block">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={previewUrl} alt="Uploaded chest X-ray" className="max-h-80 rounded-lg" />
            {result && (
              <canvas
                ref={canvasRef}
                className="absolute left-0 top-0 h-full w-full rounded-lg"
                style={{ imageRendering: "pixelated" }}
              />
            )}
          </div>

          {result && (
            <div className="mt-4 flex flex-col gap-3">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium capitalize text-gray-800 dark:text-gray-100">{result.prediction}</span>
                <span className="text-sm text-gray-500 dark:text-gray-400">{result.confidence_pct}% confidence</span>
              </div>

              {!result.clinically_meaningful && (
                <div className="rounded-lg border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-800 dark:bg-amber-950/40 dark:text-amber-200">
                  <p className="font-semibold">⚠ Not clinically meaningful</p>
                  <p className="mt-1">{result.warning}</p>
                  <p className="mt-1 text-xs">
                    Cross-validated accuracy: {(result.model_cv_accuracy * 100).toFixed(0)}% ± {(result.model_cv_accuracy_std * 100).toFixed(0)}% on {result.model_trained_on_n_images} total images (5-fold CV).
                  </p>
                </div>
              )}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
