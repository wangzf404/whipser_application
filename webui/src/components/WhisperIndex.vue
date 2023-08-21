<template>
  <el-container>
    <el-header>音视频转录工具</el-header>
    <el-main>
      <el-row :gutter="20">
        <el-col :span="12">
          <span>基础地址: </span>
          <el-input v-model="baseUrl" placeholder="请输入地址" style="display: inline-block; width: 400px;"></el-input>
        </el-col>
        <el-col :span="12">
          <span>WebSocket: </span>
          <el-input v-model="WebSocketUrl" placeholder="请输入WebSocket地址"
            style="display: inline-block; width: 400px;"></el-input>
        </el-col>
      </el-row>
      <el-tabs v-model="activeName" @tab-click="handleClick">
        <el-tab-pane name="upload">
          <span slot="label"><i class="el-icon-upload"></i>文件上传</span>
          <AudioUpload :baseUrl="baseUrl"></AudioUpload>
        </el-tab-pane>
        <el-tab-pane name="online">
          <span slot="label"><i class="el-icon-watch-1"></i>在线视频</span>
          <OnlineVideo :baseUrl="baseUrl"></OnlineVideo>
        </el-tab-pane>
        <el-tab-pane name="mic">
          <span slot="label"><i class="el-icon-mic"></i>麦克风</span>
          <AudioMicrophone :baseUrl="baseUrl" :WebSocketUrl="WebSocketUrl"></AudioMicrophone>
        </el-tab-pane>
      </el-tabs>
    </el-main>
  </el-container>
</template>
<script>
import AudioUpload from './AudioUpload.vue';
import AudioMicrophone from './AudioMicrophone.vue';
import OnlineVideo from './OnlineVideo.vue';

export default {

  data() {
    return {
      activeName: 'upload',
      baseUrl: 'http://127.0.0.1:5000',
      WebSocketUrl: 'ws://localhost:9090'
    };
  },

  components: {
    AudioUpload,
    AudioMicrophone,
    OnlineVideo
  },

  methods: {
    handleClick(tab, event) {
      console.log(tab, event);
    }
  }
}
</script>
<style></style>