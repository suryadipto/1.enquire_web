Highcharts.chart('container-representativeness', {
    chart: {
        type: 'bar',
        marginLeft: 150
    },
    
    //colors: ['#ff0000', '#00ff00', '#0000ff'],
    
    title: {
        text: 'Most popular ideas by April 2016'
    },
    exporting: {
    enabled: true
  },
    subtitle: {
        //text: 'Source: <a href="https://highcharts.uservoice.com/forums/55896-highcharts-javascript-api">UserVoice</a>'
        text: 'Top 20 terms'
    },
    xAxis: {
        type: 'category',
        title: {
            text: null
        },
        min: 0,
        max: 4,
        scrollbar: {
            enabled: true
        },
        tickLength: 0
    },
    yAxis: {
        min: 0,
        max: 1200,
        title: {
            text: 'Votes',
            align: 'high'
        }
    },
    plotOptions: {
        bar: {
            dataLabels: {
                enabled: true
            }
        }
    },
    legend: {
        enabled: false
    },
    credits: {
        enabled: false
    },
    series: [{
        name: 'Votes',
        data: [
            ['Gantt chart', 1000],
            ['Autocalculation and plotting of trend lines', 575],
            ['Allow navigator to have multiple data series', 523],
            ['Implement dynamic font size', 427],
            ['Multiple axis alignment control', 399],
            ['Stacked area (spline etc) in irregular datetime series', 309],
            ['Adapt chart height to legend height', 278],
            ['Export charts in excel sheet', 239],
            ['Toggle legend box', 235],
            ['Venn Diagram', 203],
            ['Add ability to change Rangeselector position', 182],
            ['Draggable legend box', 157],
            ['Sankey Diagram', 149],
            ['Add Navigation bar for Y-Axis in Highcharts Stock', 144],
            ['Grouped x-axis', 143],
            ['ReactJS plugin', 137],
            ['3D surface charts', 134],
            ['Draw lines over a stock chart, for analysis purpose', 118],
            ['Data module for database tables', 118],
            ['Draggable points', 117]
        ]
    }]
  });



























// var container = document.createElement('div');
// document.body.appendChild(container);

var charts = {}; // global variable

var renderTo = 'container-1';
charts[renderTo] = new Highcharts.Chart({
    chart: {
          renderTo: renderTo,
          height: 400
    },
    xAxis: {
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    },

    series: [{
        data: [29.9, 71.5, 106.4, 129.2, 144.0, 176.0, 135.6, 148.5, 216.4, 194.1, 95.6, 54.4]
    }]
});











































var dirDist50 = "#E8544E",
  dirDist10 = "#FFD265",
  dirDistLess10 = "#2AA775";

Highcharts.chart("container", {
  chart: {
    type: "networkgraph",
    marginTop: 80
  },

  title: {
    text: "South Korea domestic flight routes"
  },

  tooltip: {
    formatter: function () {
      var info = "";
      switch (this.color) {
        case dirDist50:
          console.log(dirDist50);
          info = "is an aiport <b>more than 50</b> direct distinations";
          break;
        case dirDist10:
          console.log(dirDist10);
          info = "is an aiport <b>more than 10</b> direct distinations";
          break;
        case dirDistLess10:
          console.log(dirDistLess10);
          info = "is an aiport <b>less than 10</b> direct distinations";
          break;
      }
      return "<b>" + this.key + "</b>: " + info;
    }
  },

  plotOptions: {
    networkgraph: {
      keys: ["from", "to"],
      layoutAlgorithm: {
        enableSimulation: true,
        integration: "verlet",
        linkLength: 100
      }
    }
  },

  series: [
    {
      marker: {
        radius: 13
      },
      dataLabels: {
        enabled: true,
        linkFormat: "",
        allowOverlap: true,
        style: {
          textOutline: false
        }
      },
      data: [
        ["Seoul ICN", "Daegu"],
        ["Seoul ICN", "Busan"],
        ["Busan", "Seoul GMP"],
        ["Busan", "Yangyang"],

        ["Daegu", "Seoul GMP"],
        ["Daegu", "Jeju"],

        ["Seoul GMP", "Gwangju"],
        ["Seoul GMP", "Yeosu"],
        ["Seoul GMP", "Sacheon"],
        ["Seoul GMP", "Ulsan"],
        ["Seoul GMP", "Pohang"],

        ["Jeju", "Gwangju"],
        ["Jeju", "Gunsan"],
        ["Jeju", "Wonju"],
        ["Jeju", "Yangyang"],
        ["Jeju", "Daegu"],
        ["Jeju", "Yeosu"],
        ["Jeju", "Sacheon"],
        ["Jeju", "Ulsan"],
        ["Jeju", "Busan"],
        ["Jeju", "Cheongju"]
      ],
      nodes: [
        {
          id: "Seoul ICN",
          marker: {
            radius: 30
          },
          color: dirDist50
        },
        {
          id: "Daegu",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Busan",
          marker: {
            radius: 30
          },
          color: dirDist50
        },
        {
          id: "Seoul GMP",
          marker: {
            radius: 20
          },
          color: dirDist10
        },
        {
          id: "Jeju",
          marker: {
            radius: 30
          },
          color: dirDist50
        },
        {
          id: "Gwangju",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Yeosu",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Sacheon",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Ulsan",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Pohang",
          marker: {
            radius: 20
          },
          color: dirDist10
        },
        {
          id: "Gunsan",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Wonju",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Yangyang",
          marker: {
            radius: 10
          },
          color: dirDistLess10
        },
        {
          id: "Cheongju",
          marker: {
            radius: 20
          },
          color: dirDist10
        }
      ]
    }
  ]
});
