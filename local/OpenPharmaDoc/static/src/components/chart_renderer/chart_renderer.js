/** @odoo-module **/

import {registry} from "@web/core/registry";
import {Layout} from "@web/search/layout";
import {getDefaultConfig} from "@web/views/view";
import {loadJS} from '@web/core/assets'

import {Component, useSubEnv, useState, onWillStart, useRef, onMounted} from "@odoo/owl";

export class OwlChartRenderer extends Component {
    setup() {

        this.chartRef = useRef('chart')

        // this.state = useState({
        //     title: this.props.title,
        //     data: this.props.data,
        //     type: this.props.type
        // })

        onWillStart(async () => {
            await loadJS('/OpenPharmaDoc/static/src/js/echarts.min.js')
        })

        onMounted(() => {
            console.log('Chart Renderer')
            const chartContainer = this.chartRef.el;
            const myChart = echarts.init(chartContainer, null, {devicePixelRatio: 2, height: 450, width: 900});
            this.render(myChart)
            // window.addEventListener('resize', () => {
            //     myChart.resize();
            // });
        })
    }

    render(myChart) {
        const graph = {
            "categories": [
                {
                    "name": "文档"
                },
                {
                    "name": "检验"
                }
            ],
            "nodes": [
                {
                    "category": 0,
                    "id": "d_1",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-CN.docx"
                },
                {
                    "category": 0,
                    "id": "d_2",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-CN.docx"
                },
                {
                    "category": 0,
                    "id": "d_3",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-EN.docx"
                },
                {
                    "category": 0,
                    "id": "d_4",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-EN.docx"
                },
                {
                    "category": 0,
                    "id": "d_5",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-CN.docx"
                },
                {
                    "category": 0,
                    "id": "d_6",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-CN.docx"
                },
                {
                    "category": 0,
                    "id": "d_7",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-EN.docx"
                },
                {
                    "category": 0,
                    "id": "d_8",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-EN.docx"
                },
                {
                    "category": 0,
                    "id": "d_9",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-EN.docx"
                },
                {
                    "category": 0,
                    "id": "d_10",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-EN.docx"
                },
                {
                    "category": 0,
                    "id": "d_11",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-CN.docx"
                },
                {
                    "category": 1,
                    "id": "a_2",
                    "value": 4,
                    "symbolSize": 4,
                    "name": "检验名称"
                },
                {
                    "category": 1,
                    "id": "a_4",
                    "value": 4,
                    "symbolSize": 4,
                    "name": "检验名称"
                },
                {
                    "category": 1,
                    "id": "a_6",
                    "value": 4,
                    "symbolSize": 4,
                    "name": "检验名称"
                },
                {
                    "category": 1,
                    "id": "a_8",
                    "value": 39,
                    "symbolSize": 39,
                    "name": "highly sensitive pregnancy test (urine)"
                },
                {
                    "category": 1,
                    "id": "a_10",
                    "value": 12,
                    "symbolSize": 12,
                    "name": "高灵敏度妊娠试验（尿液）"
                },
                {
                    "category": 1,
                    "id": "a_16",
                    "value": 12,
                    "symbolSize": 12,
                    "name": "高灵敏度妊娠试验（尿液）"
                },
                {
                    "category": 0,
                    "id": "d_12",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-CN.docx"
                },
                {
                    "category": 0,
                    "id": "d_13",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-EN.docx"
                },
                {
                    "category": 1,
                    "id": "a_1",
                    "value": 4,
                    "symbolSize": 4,
                    "name": "检验名称"
                },
                {
                    "category": 1,
                    "id": "a_3",
                    "value": 4,
                    "symbolSize": 4,
                    "name": "检验名称"
                },
                {
                    "category": 1,
                    "id": "a_5",
                    "value": 4,
                    "symbolSize": 4,
                    "name": "检验名称"
                },
                {
                    "category": 1,
                    "id": "a_7",
                    "value": 39,
                    "symbolSize": 39,
                    "name": "highly sensitive pregnancy test (urine)"
                },
                {
                    "category": 1,
                    "id": "a_9",
                    "value": 39,
                    "symbolSize": 39,
                    "name": "highly sensitive pregnancy test (urine)"
                },
                {
                    "category": 1,
                    "id": "a_15",
                    "value": 39,
                    "symbolSize": 39,
                    "name": "highly sensitive pregnancy test (urine)"
                },
                {
                    "category": 0,
                    "id": "d_14",
                    "value": 30,
                    "symbolSize": 30,
                    "name": "MK-3543-007-00-DEMO-EN.docx"
                }
            ],
            "links": [
                {
                    "source": "d_11",
                    "target": "a_2"
                },
                {
                    "source": "d_11",
                    "target": "a_4"
                },
                {
                    "source": "d_11",
                    "target": "a_6"
                },
                {
                    "source": "d_11",
                    "target": "a_8"
                },
                {
                    "source": "d_11",
                    "target": "a_10"
                },
                {
                    "source": "d_11",
                    "target": "a_16"
                },
                {
                    "source": "d_13",
                    "target": "a_1"
                },
                {
                    "source": "d_13",
                    "target": "a_3"
                },
                {
                    "source": "d_13",
                    "target": "a_5"
                },
                {
                    "source": "d_13",
                    "target": "a_7"
                },
                {
                    "source": "d_13",
                    "target": "a_9"
                },
                {
                    "source": "d_13",
                    "target": "a_15"
                }
            ]
        }
        const option = {
            title: {
                text: 'Les Miserables',
                subtext: 'Default layout',
                top: 'bottom',
                left: 'right'
            },
            tooltip: {},
            legend: [
                {
                    // selectedMode: 'single',
                    data: graph.categories.map(function (a) {
                        return a.name;
                    })
                }
            ],
            series: [
                {
                    name: 'Les Miserables',
                    type: 'graph',
                    layout: 'force',
                    data: graph.nodes,
                    links: graph.links,
                    categories: graph.categories,
                    roam: true,
                    label: {
                        position: 'right'
                    },
                    force: {
                        repulsion: 100
                    }
                }
            ]
        };

        // var graph = {
        //     "categories": [
        //         {
        //             "name": "文档"
        //         },
        //         {
        //             "name": "检验"
        //         }
        //     ],
        //     "nodes": [
        //         {
        //             "category": 0,
        //             "id": "d_1",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-CN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_2",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-CN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_3",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-EN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_4",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-EN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_5",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-CN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_6",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-CN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_7",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-EN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_8",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-EN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_9",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-EN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_10",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-EN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_11",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-CN.docx"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_2",
        //             "value": 4,
        //             "symbolSize": 4,
        //             "name": "检验名称"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_4",
        //             "value": 4,
        //             "symbolSize": 4,
        //             "name": "检验名称"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_6",
        //             "value": 4,
        //             "symbolSize": 4,
        //             "name": "检验名称"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_8",
        //             "value": 39,
        //             "symbolSize": 39,
        //             "name": "highly sensitive pregnancy test (urine)"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_10",
        //             "value": 12,
        //             "symbolSize": 12,
        //             "name": "高灵敏度妊娠试验（尿液）"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_16",
        //             "value": 12,
        //             "symbolSize": 12,
        //             "name": "高灵敏度妊娠试验（尿液）"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_12",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-CN.docx"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_13",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-EN.docx"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_1",
        //             "value": 4,
        //             "symbolSize": 4,
        //             "name": "检验名称"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_3",
        //             "value": 4,
        //             "symbolSize": 4,
        //             "name": "检验名称"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_5",
        //             "value": 4,
        //             "symbolSize": 4,
        //             "name": "检验名称"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_7",
        //             "value": 39,
        //             "symbolSize": 39,
        //             "name": "highly sensitive pregnancy test (urine)"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_9",
        //             "value": 39,
        //             "symbolSize": 39,
        //             "name": "highly sensitive pregnancy test (urine)"
        //         },
        //         {
        //             "category": 1,
        //             "id": "a_15",
        //             "value": 39,
        //             "symbolSize": 39,
        //             "name": "highly sensitive pregnancy test (urine)"
        //         },
        //         {
        //             "category": 0,
        //             "id": "d_14",
        //             "value": 30,
        //             "symbolSize": 30,
        //             "name": "MK-3543-007-00-DEMO-EN.docx"
        //         }
        //     ],
        //     "links": [
        //         {
        //             "source": "d_11",
        //             "target": "a_2"
        //         },
        //         {
        //             "source": "d_11",
        //             "target": "a_4"
        //         },
        //         {
        //             "source": "d_11",
        //             "target": "a_6"
        //         },
        //         {
        //             "source": "d_11",
        //             "target": "a_8"
        //         },
        //         {
        //             "source": "d_11",
        //             "target": "a_10"
        //         },
        //         {
        //             "source": "d_11",
        //             "target": "a_16"
        //         },
        //         {
        //             "source": "d_13",
        //             "target": "a_1"
        //         },
        //         {
        //             "source": "d_13",
        //             "target": "a_3"
        //         },
        //         {
        //             "source": "d_13",
        //             "target": "a_5"
        //         },
        //         {
        //             "source": "d_13",
        //             "target": "a_7"
        //         },
        //         {
        //             "source": "d_13",
        //             "target": "a_9"
        //         },
        //         {
        //             "source": "d_13",
        //             "target": "a_15"
        //         }
        //     ]
        // }
        // const option = {
        //     title: {
        //         text: 'Les Miserables',
        //         subtext: 'Default layout',
        //         top: 'bottom',
        //         left: 'right'
        //     },
        //     tooltip: {},
        //     legend: [
        //         {
        //             // selectedMode: 'single',
        //             data: graph.categories.map(function (a) {
        //                 return a.name;
        //             })
        //         }
        //     ],
        //     series: [
        //         {
        //             name: 'Les Miserables',
        //             type: 'graph',
        //             layout: 'force',
        //             data: graph.nodes,
        //             links: graph.links,
        //             categories: graph.categories,
        //             roam: true,
        //             label: {
        //                 position: 'right'
        //             },
        //             force: {
        //                 repulsion: 100
        //             }
        //         }
        //     ]
        // };

        myChart.setOption(option);
    }

}

OwlChartRenderer
    .template = "owl.knowledge_graph";
// OwlChartRenderer.components = { Layout };

registry
    .category(
        "actions"
    ).add(
    "owl.knowledge_graph"
    ,
    OwlChartRenderer
)
;