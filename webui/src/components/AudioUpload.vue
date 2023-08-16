<template>
    <el-row v-loading="loading">
        <el-col :span="8">
            <el-form ref="form" :model="form" label-width="120px" label-position="left">
                <el-form-item label="文件上传:">
                    <el-upload class="upload-demo" :action="uploadUrl" :on-success="handleUploadSuccess"
                        :before-upload="beforeUpload" :file-list="fileList" :limit="1" :on-exceed="handleExceed">
                        <el-button size="small" type="primary">点击上传</el-button>
                    </el-upload>
                </el-form-item>
                <el-form-item label="选择模型:">
                    <el-select v-model="form.model" placeholder="请选择">
                        <el-option label="tiny" value="tiny"></el-option>
                        <el-option label="base" value="base"></el-option>
                        <el-option label="small" value="small"></el-option>
                        <el-option label="medium" value="medium"></el-option>
                        <el-option label="large" value="large"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="源语言:">
                    <el-select v-model="form.language" placeholder="请选择">
                        <el-option label="自动识别" value="auto"></el-option>
                        <el-option label="中文" value="zh"></el-option>
                        <el-option label="英文" value="en"></el-option>
                        <el-option label="日文" value="ja"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="双语字幕:">
                    <el-checkbox v-model="form.translator">开启双语字幕</el-checkbox>
                </el-form-item>
                <el-form-item>
                    <!-- <el-button type="primary" @click="resetForm">重置</el-button> -->
                    <el-button type="primary" @click="submitForm">开始转写</el-button>
                </el-form-item>
            </el-form>
        </el-col>
        <el-col :span="8">
            <video ref="player" class="plyr" controls>
                <source src="" type="">
                <track kind="captions" label="中文" src="" srclang="zh" default>
            </video>
        </el-col>
        <el-col :span="8">
            <div style="max-height: 300px; overflow: auto;font-size: 20px;">
                <div v-html="txt_content"></div>
            </div>
        </el-col>
    </el-row>
</template>
  
<script>
import axios from 'axios';
import 'plyr/dist/plyr.css'; // Import Plyr styles
import Plyr from 'plyr'; // Import Plyr library

export default {
    props: {
        baseUrl: String
    },
    data() {
        return {
            form: {
                model: 'tiny',
                language: 'auto',
                translator: false
            },
            player: null,

            fileList: [],
            filePath: '',
            uploadUrl: '',
            loading: false,
            txt_content: '',
        };
    },
    components: {
        Plyr
    },
    created() {
        this.uploadUrl = this.baseUrl + '/upload_file'
    },
    mounted() {
        this.initPlyr();
    },
    methods: {
        initPlyr() {
            this.player = new Plyr(this.$refs.player, {
                // 自动播放
                autoplay: false,
                // 默认音量（0 到 1 之间的值）
                volume: 0.5,
                captions: { active: true, language: 'auto' },
                controls: [
                    'play-large',
                    'play',
                    'progress',
                    'current-time',
                    'volume',
                    'captions',
                    'settings',
                    'fullscreen',
                ]
            });
        },
        // 获取字幕内容
        getSubtitleContent(sub_path) {
            axios.get(this.baseUrl + '/sub?sub_path=' + (sub_path.replace('.mp4', '.vtt')))
                .then(response => {
                    this.reloadPlyr(sub_path, URL.createObjectURL(new Blob([response.data], { type: 'text/vtt' })))
                })
                .catch(error => {
                    console.error('Failed to load subtitle:', error);
                });
        },
        reloadPlyr(videoUrl, subSrc) {
            this.player.source = {
                type: 'video',
                sources: [
                    {
                        src: this.baseUrl + '/video?file_path=' + videoUrl,
                        type: 'video/mp4',
                    },
                ],
                tracks: [
                    {
                        kind: 'captions',
                        label: '中文',
                        src: subSrc,
                        srclang: 'zh',
                        default: true
                    }
                ],
            };
        },
        handleUploadSuccess(response, file) {
            if (response.code === 200) {
                this.fileList = [file];
                this.filePath = response.file_path
                this.$message.success('文件上传成功');
            }
        },
        beforeUpload(file) { },
        handleExceed(files, fileList) {
            this.$message.warning('只能上传一个文件');
        },
        resetForm() {
            this.$refs.form.resetFields();
        },
        submitForm() {
            this.$refs.form.validate(valid => {
                if (valid && this.filePath !== '') {
                    // 提交表单逻辑
                    const formData = {
                        filePath: this.filePath,
                        model: this.form.model,
                        language: this.form.language,
                        translator: this.form.translator
                    };
                    this.loading = true;
                    axios.post(this.baseUrl + '/transcription', formData)
                        .then(response => {
                            this.txt_content = response.data.txt_content.replace(/\n/g, '<br/>');
                            this.getSubtitleContent(this.filePath)
                        })
                        .catch(error => {
                            this.$message.error('表单提交失败');
                        })
                        .finally(() => {
                            this.loading = false;
                        });
                } else {
                    this.$message.error('表单验证失败');
                }
            });
        }
    }
};
</script>
<style>
    .plyr {
      max-width: 100%;
      max-height: 100vh;
    }
</style>