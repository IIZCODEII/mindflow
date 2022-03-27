
var socket = io({transports: ["polling"],
                forceNew: true});




var ctxLive = document.getElementById('liveChart');
const config_live = {
  type: 'line',             // 'line', 'bar', 'bubble' and 'scatter' types are supported
  data: {
    datasets: [{  
        label:'',  
        data: [],
        borderColor: 'rgb(222, 49, 99)',              // empty at the beginning
    },]
  },
  options: {
    plugins: {
      title: {
        display: true,
        text: 'Live Emotion Probability Chart'
      }
  },
    scales: {
      x: {
        type: 'realtime',   // x axis will auto-scroll from right to left
        realtime: {         // per-axis options
          duration: 20000,  // data in the past 20000 ms will be displayed
          refresh: 1000,    // onRefresh callback will be called every 1000 ms
          delay: 1000,      // delay of 1000 ms, so upcoming values are known before plotting a line
          pause: false,     // chart is not paused
          ttl: undefined,   // data will be automatically deleted as it disappears off the chart
          frameRate: 30,    // data points are drawn 30 times every second
        },
      y: {
        suggestedMin: 0,
        suggestedMax: 100

      }  
      }
    }
  }
};

var labels = ['neutral', 'happy', 'sad', 'surprise', 'fear', 'disgust', 'anger', 'contempt'];
var ctxRadar = document.getElementById('radarChart');
const config_radar = {
  type: 'radar',             // 'line', 'bar', 'bubble' and 'scatter' types are supported
  data: {
    labels:labels,
    datasets: [{  
        label:'Session Average Emotional Profile',  
        data: [],
        fill: true,
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        borderColor: 'rgb(255, 99, 132)',             // empty at the beginning
    },]
  }
};

var spectrum = ['positive','neutral','negative'];
var ctxDoughnut = document.getElementById('doughnutChart');
const config_doughnut = {
  type: 'doughnut',             // 'line', 'bar', 'bubble' and 'scatter' types are supported
  data: {
    labels:spectrum,
    datasets: [{  
        label:'Average Emotional Spectrum',  
        data: [],
        fill: true,
        backgroundColor: [
            'rgb(51, 255, 136)',
            'rgb(41, 128, 185)',
            'rgb(255, 51, 106)'
    ],
        borderColor: 'rgb(255, 99, 132)',             // empty at the beginning
    },]
  }
};       



var liveChart = new Chart(ctxLive, config_live);
var radarChart = new Chart(ctxRadar, config_radar);
var doughnutChart = new Chart(ctxDoughnut, config_doughnut);

socket.on('connect', function() {
    console.log("Connected...!", socket.connected)
});


socket.emit('frame', "init");
console.log('init ok');

socket.on('response_back', function(data) {

    console.log('response_back ok');
    console.log(data.emotion);
    console.log(data.emotion_prob);
    const image_id = document.getElementById('image');
    image_id.src = data.image;

    date = Date.now();

    console.log(data.probs_avg)

    if (data.probs != null){

         liveChart.data.datasets[0].data.push({
         x: date,
         y: data.emotion_prob*100
        });

        liveChart.data.datasets[0].label = data.emotion;
        liveChart.update('quiet');

        document.getElementById("liveNeutral").innerHTML = Math.round((data.probs[0] + Number.EPSILON) * 10000)/100 ;
        document.getElementById("liveHappy").innerHTML = Math.round((data.probs[1] + Number.EPSILON) * 10000)/100 ;
        document.getElementById("liveSad").innerHTML = Math.round((data.probs[2] + Number.EPSILON) * 10000)/100 ;
        document.getElementById("liveSurprise").innerHTML = Math.round((data.probs[3] + Number.EPSILON) * 10000)/100 ;
        document.getElementById("liveFear").innerHTML = Math.round((data.probs[4] + Number.EPSILON) * 10000)/100 ;
        document.getElementById("liveDisgust").innerHTML = Math.round((data.probs[5] + Number.EPSILON) * 10000)/100 ;
        document.getElementById("liveAnger").innerHTML = Math.round((data.probs[6] + Number.EPSILON) * 10000)/100 ;
        document.getElementById("liveContempt").innerHTML = Math.round((data.probs[7] + Number.EPSILON) * 10000)/100 ;


        radarChart.data.datasets[0].data = data.probs_avg;
        radarChart.update('quiet');

        doughnutChart.data.datasets[0].data = data.emotion_spectrum;
        doughnutChart.update('quiet');


   };

    


   


});


