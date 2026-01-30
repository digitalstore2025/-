/**
 * QudsCast AI - Backend Server
 * Arabic News Video & Radio Automation Platform
 */

const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const { exec, spawn } = require('child_process');
const util = require('util');

const execPromise = util.promisify(exec);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use('/storage', express.static(path.join(__dirname, '../storage')));

// Storage paths
const STORAGE_PATH = path.join(__dirname, '../storage');
const AUDIO_PATH = path.join(STORAGE_PATH, 'audio');
const VIDEO_PATH = path.join(STORAGE_PATH, 'videos');
const VOICES_PATH = path.join(STORAGE_PATH, 'voices');
const JINGLES_PATH = path.join(STORAGE_PATH, 'jingles');

// Ensure directories exist
[AUDIO_PATH, VIDEO_PATH, VOICES_PATH, JINGLES_PATH].forEach(dir => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Video format presets for different platforms
const VIDEO_FORMATS = {
  // Instagram Reels / TikTok / Stories
  'reels': {
    name: 'Instagram Reels',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    icon: '📱'
  },
  // Instagram Feed (Square)
  'feed_square': {
    name: 'Instagram Feed (مربع)',
    width: 1080,
    height: 1080,
    aspectRatio: '1:1',
    icon: '⬜'
  },
  // Instagram Feed (Portrait)
  'feed_portrait': {
    name: 'Instagram Feed (عمودي)',
    width: 1080,
    height: 1350,
    aspectRatio: '4:5',
    icon: '📋'
  },
  // Instagram Feed (Landscape)
  'feed_landscape': {
    name: 'Instagram Feed (أفقي)',
    width: 1080,
    height: 566,
    aspectRatio: '1.91:1',
    icon: '🖼️'
  },
  // YouTube Shorts
  'youtube_shorts': {
    name: 'YouTube Shorts',
    width: 1080,
    height: 1920,
    aspectRatio: '9:16',
    icon: '▶️'
  },
  // Facebook Feed
  'facebook': {
    name: 'Facebook',
    width: 1080,
    height: 1080,
    aspectRatio: '1:1',
    icon: '📘'
  },
  // Twitter/X
  'twitter': {
    name: 'Twitter/X',
    width: 1280,
    height: 720,
    aspectRatio: '16:9',
    icon: '🐦'
  }
};

// News Script Prompt (Locked)
const NEWS_SCRIPT_PROMPT = `أنت مذيع أخبار في إذاعة القدس.
حوّل الخبر التالي إلى:
- افتتاحية إذاعية رسمية
- نص إذاعي من 75 كلمة
- Caption إخباري مهني
- 5 Hashtags عربية
النبرة: هادئة، واثقة، مهنية
اللغة: عربية فصحى
بدون شرح.`;

/**
 * Generate news script using local AI (simulated for demo)
 */
async function generateNewsScript(newsText) {
  // For demo: create structured broadcast script
  const intro = "أهلاً بكم في نشرة أخبار إذاعة القدس";
  const wordCount = newsText.split(/\s+/).length;

  // Validate and format the script
  let broadcastText = newsText;
  if (wordCount > 100) {
    broadcastText = newsText.split(/\s+/).slice(0, 75).join(' ') + '...';
  }

  const script = {
    intro: intro,
    body: broadcastText,
    fullScript: `${intro}.\n\n${broadcastText}\n\nشكراً لمتابعتكم، وإلى اللقاء في نشرة أخبار قادمة.`,
    caption: `📰 عاجل | ${broadcastText.substring(0, 150)}...`,
    hashtags: ['#أخبار_القدس', '#إذاعة_القدس', '#فلسطين', '#عاجل', '#أخبار_اليوم']
  };

  return script;
}

/**
 * Generate voice using Coqui TTS (XTTS v2)
 */
async function generateVoice(text, outputPath, jobId) {
  const scriptPath = path.join(STORAGE_PATH, `script_${jobId}.txt`);

  // Write script to file
  fs.writeFileSync(scriptPath, text, 'utf8');

  // Check if Python TTS script exists
  const ttsScript = path.join(__dirname, 'tts/generate_voice.py');
  const voiceSample = path.join(VOICES_PATH, 'imad_nour.wav');

  // Use espeak for Arabic TTS as fallback (free)
  try {
    // Try using piper TTS (free, fast, good quality)
    const piperCmd = `echo "${text}" | piper --model ar_JO-kareem-medium --output_file ${outputPath}`;
    await execPromise(piperCmd);
  } catch (err) {
    // Fallback to espeak-ng for Arabic
    try {
      const espeakCmd = `espeak-ng -v ar -s 130 -w ${outputPath} -f ${scriptPath}`;
      await execPromise(espeakCmd);
    } catch (err2) {
      // Final fallback: Use Python gTTS
      const gttsScript = `
from gtts import gTTS
import sys
text = open('${scriptPath}', 'r', encoding='utf-8').read()
tts = gTTS(text=text, lang='ar', slow=False)
tts.save('${outputPath.replace('.wav', '.mp3')}')
`;
      const pyScriptPath = path.join(STORAGE_PATH, `tts_${jobId}.py`);
      fs.writeFileSync(pyScriptPath, gttsScript);

      try {
        await execPromise(`python3 ${pyScriptPath}`);
        // Convert mp3 to wav
        const mp3Path = outputPath.replace('.wav', '.mp3');
        if (fs.existsSync(mp3Path)) {
          await execPromise(`ffmpeg -y -i ${mp3Path} ${outputPath}`);
        }
      } catch (err3) {
        console.error('TTS generation failed:', err3);
        throw new Error('فشل توليد الصوت');
      }

      // Cleanup
      if (fs.existsSync(pyScriptPath)) fs.unlinkSync(pyScriptPath);
    }
  }

  // Cleanup script file
  if (fs.existsSync(scriptPath)) fs.unlinkSync(scriptPath);

  return outputPath;
}

/**
 * Generate radio MP3 with jingles
 */
async function generateRadioMP3(voicePath, outputPath, jobId) {
  const introPath = path.join(JINGLES_PATH, 'intro.mp3');
  const outroPath = path.join(JINGLES_PATH, 'outro.mp3');

  // Check if jingles exist, if not create silent placeholders
  if (!fs.existsSync(introPath)) {
    await execPromise(`ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 2 ${introPath}`);
  }
  if (!fs.existsSync(outroPath)) {
    await execPromise(`ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t 2 ${outroPath}`);
  }

  // Ensure voice file exists
  const voiceFile = fs.existsSync(voicePath) ? voicePath : voicePath.replace('.wav', '.mp3');

  if (!fs.existsSync(voiceFile)) {
    throw new Error('ملف الصوت غير موجود');
  }

  // Concatenate with jingles and normalize
  const filterComplex = `[0:a][1:a][2:a]concat=n=3:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[outa]`;

  const ffmpegCmd = `ffmpeg -y -i "${introPath}" -i "${voiceFile}" -i "${outroPath}" -filter_complex "${filterComplex}" -map "[outa]" "${outputPath}"`;

  try {
    await execPromise(ffmpegCmd);
  } catch (err) {
    // Fallback: simple concatenation without normalization
    const simpleCmd = `ffmpeg -y -i "${introPath}" -i "${voiceFile}" -i "${outroPath}" -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[outa]" -map "[outa]" "${outputPath}"`;
    await execPromise(simpleCmd);
  }

  return outputPath;
}

/**
 * Generate video for specified platform
 */
async function generateVideo(audioPath, caption, outputPath, jobId, platform = 'reels') {
  const format = VIDEO_FORMATS[platform] || VIDEO_FORMATS['reels'];
  const { width, height } = format;

  const bgPath = path.join(STORAGE_PATH, `bg_${width}x${height}.jpg`);
  const captionPath = path.join(STORAGE_PATH, `caption_${jobId}.txt`);

  // Write caption to file
  fs.writeFileSync(captionPath, caption, 'utf8');

  // Create background image for this format if not exists
  if (!fs.existsSync(bgPath)) {
    const createBgCmd = `ffmpeg -y -f lavfi -i "color=c=#1a1a2e:s=${width}x${height}:d=1" -vframes 1 "${bgPath}"`;
    await execPromise(createBgCmd);
  }

  // Get audio duration
  let duration = 30;
  try {
    const durationCmd = `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${audioPath}"`;
    const { stdout } = await execPromise(durationCmd);
    duration = Math.ceil(parseFloat(stdout)) + 1;
  } catch (err) {
    console.log('Could not get audio duration, using default');
  }

  // Escape caption for ffmpeg
  const escapedCaption = caption
    .replace(/'/g, "'\\''")
    .replace(/:/g, '\\:')
    .replace(/\[/g, '\\[')
    .replace(/\]/g, '\\]')
    .substring(0, 200);

  // Calculate text box position based on aspect ratio
  const isVertical = height > width;
  const isSquare = height === width;

  let textBoxY, textBoxHeight, textY, fontSize;

  if (isVertical) {
    // Vertical (Reels, Stories)
    textBoxY = 'ih-280';
    textBoxHeight = 180;
    textY = 'h-220';
    fontSize = 32;
  } else if (isSquare) {
    // Square (Feed)
    textBoxY = 'ih-200';
    textBoxHeight = 140;
    textY = 'h-150';
    fontSize = 28;
  } else {
    // Horizontal (Landscape)
    textBoxY = 'ih-120';
    textBoxHeight = 100;
    textY = 'h-90';
    fontSize = 24;
  }

  const ffmpegCmd = `ffmpeg -y -loop 1 -i "${bgPath}" -i "${audioPath}" \
    -vf "scale=${width}:${height},zoompan=z='min(zoom+0.0003,1.03)':d=${duration*25}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',drawbox=y=${textBoxY}:color=black@0.7:width=iw:height=${textBoxHeight}:t=fill,drawtext=text='${escapedCaption}':fontcolor=white:fontsize=${fontSize}:x=(w-text_w)/2:y=${textY}:font=Arial" \
    -t ${duration} -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 128k -pix_fmt yuv420p -shortest "${outputPath}"`;

  try {
    await execPromise(ffmpegCmd, { maxBuffer: 50 * 1024 * 1024 });
  } catch (err) {
    // Simpler fallback without text overlay
    const simpleCmd = `ffmpeg -y -loop 1 -i "${bgPath}" -i "${audioPath}" -vf "scale=${width}:${height}" -t ${duration} -c:v libx264 -preset fast -c:a aac -pix_fmt yuv420p -shortest "${outputPath}"`;
    await execPromise(simpleCmd, { maxBuffer: 50 * 1024 * 1024 });
  }

  // Cleanup
  if (fs.existsSync(captionPath)) fs.unlinkSync(captionPath);

  return { path: outputPath, format };
}

/**
 * Generate videos for multiple platforms
 */
async function generateMultipleVideos(audioPath, caption, jobId, platforms = ['reels']) {
  const results = {};

  for (const platform of platforms) {
    const outputPath = path.join(VIDEO_PATH, `video_${jobId}_${platform}.mp4`);
    const result = await generateVideo(audioPath, caption, outputPath, jobId, platform);
    results[platform] = {
      path: result.path,
      url: `/storage/videos/video_${jobId}_${platform}.mp4`,
      format: result.format
    };
  }

  return results;
}

/**
 * Process news job
 */
async function processNewsJob(newsText, jobId, platforms = ['reels']) {
  const status = {
    id: jobId,
    stage: 'init',
    progress: 0,
    error: null,
    outputs: {},
    platforms: platforms
  };

  try {
    // Stage 1: Generate script
    status.stage = 'script';
    status.progress = 10;
    const script = await generateNewsScript(newsText);
    status.outputs.script = script;
    status.progress = 20;

    // Stage 2: Generate voice
    status.stage = 'voice';
    status.progress = 30;
    const voicePath = path.join(AUDIO_PATH, `voice_${jobId}.wav`);
    await generateVoice(script.fullScript, voicePath, jobId);
    status.outputs.voicePath = voicePath;
    status.progress = 50;

    // Stage 3: Generate radio MP3 with jingles
    status.stage = 'radio';
    status.progress = 60;
    const radioPath = path.join(AUDIO_PATH, `radio_${jobId}.mp3`);
    await generateRadioMP3(voicePath, radioPath, jobId);
    status.outputs.radioPath = radioPath;
    status.outputs.radioUrl = `/storage/audio/radio_${jobId}.mp3`;
    status.progress = 70;

    // Stage 4: Generate videos for selected platforms
    status.stage = 'video';
    status.progress = 75;

    const videoResults = await generateMultipleVideos(radioPath, script.caption, jobId, platforms);
    status.outputs.videos = videoResults;

    // For backward compatibility, set primary video
    const primaryPlatform = platforms[0];
    if (videoResults[primaryPlatform]) {
      status.outputs.videoPath = videoResults[primaryPlatform].path;
      status.outputs.videoUrl = videoResults[primaryPlatform].url;
    }

    status.progress = 100;
    status.stage = 'completed';

  } catch (err) {
    status.stage = 'error';
    status.error = err.message;
    console.error('Job processing error:', err);
  }

  return status;
}

// Store active jobs
const jobs = new Map();

// API Routes

/**
 * Health check
 */
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', service: 'QudsCast AI' });
});

/**
 * Get available video formats
 */
app.get('/api/formats', (req, res) => {
  res.json(VIDEO_FORMATS);
});

/**
 * Generate news content
 */
app.post('/api/generate', async (req, res) => {
  const { newsText, platforms } = req.body;

  if (!newsText || newsText.trim().length < 10) {
    return res.status(400).json({
      error: 'يرجى إدخال نص الخبر (10 أحرف على الأقل)'
    });
  }

  // Validate platforms
  let selectedPlatforms = platforms || ['reels'];
  if (!Array.isArray(selectedPlatforms)) {
    selectedPlatforms = [selectedPlatforms];
  }
  selectedPlatforms = selectedPlatforms.filter(p => VIDEO_FORMATS[p]);
  if (selectedPlatforms.length === 0) {
    selectedPlatforms = ['reels'];
  }

  const jobId = uuidv4();

  // Start processing in background
  jobs.set(jobId, { status: 'processing', progress: 0, platforms: selectedPlatforms });

  // Return job ID immediately
  res.json({ jobId, status: 'processing', platforms: selectedPlatforms });

  // Process job
  const result = await processNewsJob(newsText, jobId, selectedPlatforms);
  jobs.set(jobId, result);
});

/**
 * Get job status
 */
app.get('/api/job/:jobId', (req, res) => {
  const { jobId } = req.params;
  const job = jobs.get(jobId);

  if (!job) {
    return res.status(404).json({ error: 'الوظيفة غير موجودة' });
  }

  res.json(job);
});

/**
 * Download file
 */
app.get('/api/download/:type/:jobId', (req, res) => {
  const { type, jobId } = req.params;
  const platform = req.query.platform || 'reels';

  let filePath;
  let fileName;

  if (type === 'mp3') {
    filePath = path.join(AUDIO_PATH, `radio_${jobId}.mp3`);
    fileName = `qudscast_radio_${jobId}.mp3`;
  } else if (type === 'mp4') {
    // Try platform-specific file first
    filePath = path.join(VIDEO_PATH, `video_${jobId}_${platform}.mp4`);
    if (!fs.existsSync(filePath)) {
      // Fallback to old format
      filePath = path.join(VIDEO_PATH, `video_${jobId}.mp4`);
    }
    const formatName = VIDEO_FORMATS[platform]?.name || platform;
    fileName = `qudscast_${platform}_${jobId}.mp4`;
  } else {
    return res.status(400).json({ error: 'نوع ملف غير صالح' });
  }

  if (!fs.existsSync(filePath)) {
    return res.status(404).json({ error: 'الملف غير موجود' });
  }

  res.download(filePath, fileName);
});

/**
 * Upload voice sample
 */
const upload = multer({
  dest: VOICES_PATH,
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB limit
});

app.post('/api/upload-voice', upload.single('voice'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'لم يتم رفع ملف' });
  }

  const targetPath = path.join(VOICES_PATH, 'imad_nour.wav');
  fs.renameSync(req.file.path, targetPath);

  res.json({ success: true, message: 'تم رفع عينة الصوت بنجاح' });
});

/**
 * Upload jingle
 */
app.post('/api/upload-jingle', upload.single('jingle'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'لم يتم رفع ملف' });
  }

  const jingleType = req.body.type || 'intro';
  const targetPath = path.join(JINGLES_PATH, `${jingleType}.mp3`);
  fs.renameSync(req.file.path, targetPath);

  res.json({ success: true, message: `تم رفع ${jingleType} بنجاح` });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).json({ error: 'خطأ في الخادم' });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔══════════════════════════════════════════╗
║     QudsCast AI - Backend Server         ║
║     Arabic News Automation Platform      ║
╠══════════════════════════════════════════╣
║  Server running on port: ${PORT}             ║
║  API: http://localhost:${PORT}/api          ║
╚══════════════════════════════════════════╝
  `);
});

module.exports = app;
