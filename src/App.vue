<template>
  <div id="app">
    <center>
      <h1>Malody/Osu BeatMap Speed Changer</h1>
      <el-upload
              class="upload-demo"
              drag
              name="file"
              :on-success="handleUploadSuccess"
              action="/api/upload_file">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text">Drag file to hear，Or <em>Click to Upload</em></div>
        <div class="el-upload__tip" slot="tip">only support file ended with .mcz and .osz</div>
      </el-upload>

      <div v-if="beatmaps.length !== 0">
        <br><br>
        <label>Select BeatMap：</label>
        <el-select v-model="index" placeholder="Please Select" style="width: 350px">
          <el-option
                  v-for="item in beatmaps"
                  :key="item.id"
                  :label="item.version"
                  :value="item.id">
          </el-option>
        </el-select>

        <br><br>
        <label>Select Speed：</label>
        <el-checkbox-group v-model="checkedSpeeds" style="max-width: 800px">
          <el-checkbox v-for="speed in speeds" :label="speed" :key="speed">{{speed}}</el-checkbox>
        </el-checkbox-group>

        <br><br>
        <el-button type="primary" style="width: 350px" @click="getBeatMaps">Generate BeatMap</el-button>
        <br><br>
        <a v-if="show_result" :href="'/api/get_file/' + result_file">Download BeatMap</a>

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

      Api.get("/get_speeds", {}, (res)=> {
        loading.close();
        this.speeds = res.speeds;
      })
  },
  methods: {
    handleUploadSuccess(res) {

      if (res.success) {
        this.$message({
          message: 'Upload Success',
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
          this.$message.error("Error occurred，generation for beatmap failed");
        }
      })
    }
  }
}
</script>
