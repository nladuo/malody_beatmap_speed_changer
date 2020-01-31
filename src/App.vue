<template>
  <div id="app">
    <center>
      <h1>Malody谱面速度修改器</h1>
      <el-upload
              class="upload-demo"
              drag
              name="file"
              :on-success="handleUploadSuccess"
              action="/api/upload_file">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
        <div class="el-upload__tip" slot="tip">只能上传malody格式的谱面（不支持osu格式）</div>
      </el-upload>

      <div v-if="beatmaps.length !== 0">
        <br><br>
        <label>选择谱面：</label>
        <el-select v-model="index" placeholder="请选择" style="width: 350px">
          <el-option
                  v-for="item in beatmaps"
                  :key="item.id"
                  :label="item.version +'-' + item.bpm"
                  :value="item.id">
          </el-option>
        </el-select>

        <br><br>
        <label>选择速度：</label>
        <el-checkbox-group v-model="checkedSpeeds" style="max-width: 800px">
          <el-checkbox v-for="speed in speeds" :label="speed" :key="speed">{{speed}}</el-checkbox>
        </el-checkbox-group>

        <br><br>
        <el-button type="primary" style="width: 350px" @click="getBeatMaps">生成谱面</el-button>

        <a v-if="show_result" :href="'/api/get_file/' + result_file">下载谱面</a>

      </div>

    </center>

  </div>
</template>

<script>
  import Api from './actions/api'
export default {
  name: 'app',
  data() {
    return{
      beatmaps:[],
      speeds: [],
      checkedSpeeds: [],
      index: 0,
      show_result: false,
      result_file: ""
    }
  },
  mounted() {
    const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });

      Api.get("/get_speeds", {
        speeds: JSON.stringify(this.checkedSpeeds),
        index: this.index
      }, (res)=> {
        loading.close();
        this.speeds = res.speeds;
      })
  },
  methods: {
    handleUploadSuccess(res) {

      if (res.success) {
        this.$message({
          message: '上传成功',
          type: 'success'
        });
        this.show_result = false;
        this.beatmaps = res.beatmaps;
        console.log(this.beatmaps);
      } else {
        this.$message.error(res.msg);
      }
    },

    getBeatMaps() {
      console.log(this.index);
      console.log(this.checkedSpeeds);


      const loading = this.$loading({
        lock: true,
        text: 'Loading',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });

      Api.get("/generate_beatmaps", {
        speeds: JSON.stringify(this.checkedSpeeds),
        index: this.index
      }, (res)=>{
        loading.close();
        if (res.success) {
          this.show_result = true;
          this.result_file = res.file;
        }else {
          this.show_result = false;
          this.$message.error("发生错误，生成谱面失败");
        }
      })
    }
  }
}
</script>
