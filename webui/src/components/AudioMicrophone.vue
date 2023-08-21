<template>
  <div>
    <el-button type="primary" @click="toggleRecording">{{ recording ? '停止录音' : '开始录音' }}</el-button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      recording: false,
      mediaRecorder: null,
      mediaStream: null,
      websocket: null,
    };
  },
  methods: {
    async startRecording() {
      try {
        // 获取麦克风音频输入
        this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // 创建 MediaRecorder
        this.mediaRecorder = new MediaRecorder(this.mediaStream);

        // 监听音频数据可用事件
        this.mediaRecorder.ondataavailable = event => {
          console.log('---------------')
          if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            console.log(event.data)
            this.websocket.send(event.data);
          }
        };

        // 开始录制
        this.mediaRecorder.start(3000);

        // 连接 WebSocket 服务器
        this.websocket = new WebSocket('ws://localhost:8765'); // 替换为实际的 WebSocket 服务器地址
      } catch (error) {
        console.error('无法访问麦克风或浏览器不支持', error);
      }

      // 更新录音状态标志
      this.recording = true;
    },
    async stopRecording() {
      // 停止录制
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop();
        this.mediaRecorder = null;
      }

      // 关闭 WebSocket 连接
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }

      // 停止音频输入
      if (this.mediaStream) {
        this.mediaStream.getTracks().forEach(track => track.stop());
        this.mediaStream = null;
      }

      // 更新录音状态标志
      this.recording = false;
    },
    toggleRecording() {
      if (this.recording) {
        this.stopRecording();
      } else {
        this.startRecording();
      }
    },
  },
  beforeDestroy() {
    // 确保在组件销毁时停止录音和关闭 WebSocket 连接
    if (this.recording) {
      this.stopRecording();
    }
  },
};
</script>