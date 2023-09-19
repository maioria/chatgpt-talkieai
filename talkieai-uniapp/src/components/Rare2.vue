<template>
  <view class="progress_box" :style="{ 'background-color': pageBg }">
    <!-- #ifdef MP-ALIPAY -->
    <canvas
      :id="id"
      :style="{ width: width + 'px', height: width / 1 + 'px' }"
      disable-scroll="true"
      @touchstart="touchStart"
      @touchmove="touchMove"
      @touchend="touchEnd"
    ></canvas>
    <!-- #endif -->
    <!-- #ifndef MP-ALIPAY -->
    <canvas
      :canvas-id="id"
      :style="{ width: width + 'px', height: width / 1 + 'px' }"
      disable-scroll="true"
      @touchstart="touchStart"
      @touchmove="touchMove"
      @touchend="touchEnd"
    ></canvas>
    <!-- #endif -->
    <slot></slot>
  </view>
</template>

<script>
export default {
  name: "Seekbar",
  props: {
    id: {
      default: "canvas",
    },
    width: {
      default: 220, //宽度
    },
    processVal: {
      default: 0, //默认进度值
    },
    max: {
      default: 100, //最大值
    },
    step: {
      default: 1, //步进值
    },
    startDeg: {
      default: 0, //开始弧度0
    },
    endDeg: {
      default: 2, //结束弧度2
    },
    innerLineWidth: {
      default: 1, //内弧宽度
    },
    innerColor: {
      default: "#49CEB0", //内弧颜色
    },
    innerLineDash: {
      default: false, // //内弧是否为虚线 Number类型,虚线的宽度
    },
    border: {
      default: 10, //外弧线宽
    },
    process: {
      default: 8, //进度圆弧宽度
    },
    colorSatrt: {
      default: "#C4C4C4", //外弧背景色，string || []
    },
    colorEnd: {
      default: () => ["#49CEB0", "#49CEB0"], //进度背景色 string || []
    },
    isCounterClockWise: {
      default: false, //是否为逆时针方向
    },
    sliderSize: {
      default: 0, //滑块大小
    },
    indoorCircleSize: {
      default: 0, //滑块内部圆大小
    },
    sliderColor: {
      default: "#FFFFFF", //滑块颜色
    },
    indoorCircleColor: {
      default: "#87ae3f", //滑块内圆颜色
    },
    isShowSlider: {
      default: true, //是否显示滑块
    },
    lock: {
      default: false, //是否可以拖动,默认锁住，不可拖动
    },
    isShowText: {
      default: true, //是否显示文字
    },
    pageBg: {
      default: "", //背景色
    },
  },
  data() {
    return {
      val: 0,
      center: this.width / 2,
      radius: this.width / 2 - 30,
      residueDeg: 2 - this.startDeg,
      animate: null,
      isDown: false, //判断手指是否在滑块上
      
      // 微信小程序会报navigator 为 undifined 错误
      // isMobile: /Android|webOS|iPhone|iPod|BlackBerry/i.test(
      //   navigator.userAgent
      // ), //设备类型判断
      p: {},
    };
  },
  mounted() {
    this.val = this.processVal;
    this.draw(this.val);
  },
  watch: {
    processVal(newVal) {
      this.val = newVal;
      this.draw(newVal);
    },
    max(newVal) {
      this.max = newVal;
      this.draw(this.val);
    },
    lock(newVal) {
      this.lock = newVal;
      this.draw(this.val);
    },
  },
  methods: {
    //绘图
    draw(value) {
      //获取canvas对象
      const ctx = uni.createCanvasContext(this.id, this);
      ctx.setLineCap("round");

      //清除画布
      ctx.clearRect(0, 0, this.width, this.width);
      ctx.save();

      let startDeg = this.isCounterClockWise
        ? Math.PI * (2 - this.startDeg)
        : Math.PI * this.startDeg;
      let endDeg = this.isCounterClockWise
        ? Math.PI * (2 - this.endDeg)
        : Math.PI * this.endDeg;

      // 绘制内层圆弧
      let innerThemeColor =
        typeof this.innerColor == "string"
          ? this.innerColor
          : this.setLinearGradient(this.innerColor, ctx);
      ctx.beginPath();
      this.innerLineDash &&
        ctx.setLineDash([this.innerLineDash, this.innerLineDash], 1);
      ctx.setLineWidth(this.innerLineWidth);
      ctx.setStrokeStyle(innerThemeColor);
      ctx.arc(
        this.center,
        this.center,
        this.radius - 30,
        startDeg,
        endDeg,
        this.isCounterClockWise
      ); // 绘制内层圆弧
      //   ctx.stroke();

      // // 绘制外侧圆弧
      ctx.beginPath();
      this.innerLineDash && ctx.setLineDash([1, 0], 1);
      ctx.setLineWidth(this.border);
      ctx.setStrokeStyle(this.colorSatrt);
      ctx.arc(
        this.center,
        this.center,
        this.radius,
        startDeg,
        endDeg,
        this.isCounterClockWise
      ); // 绘制外侧圆弧
      ctx.stroke();

      let Deg = this.valToDeg(value);

      // // 绘制可变圆弧
      let themeColor =
        typeof this.colorEnd == "string"
          ? this.colorEnd
          : this.setLinearGradient(this.colorEnd, ctx);
      ctx.beginPath();
      ctx.setLineWidth(this.process);
      ctx.setStrokeStyle(themeColor);
      ctx.arc(
        this.center,
        this.center,
        this.radius,
        startDeg,
        Deg,
        this.isCounterClockWise
      ); // 可变圆弧
      ctx.stroke();

      // 文字
      ctx.font = `${this.center / 2}px`;
      ctx.setFontSize(36);
      ctx.setFillStyle(themeColor);
      ctx.setTextAlign("center");
      ctx.setTextBaseline("middle");
      this.isShowText && ctx.fillText(this.val, this.center, this.center);

      ctx.draw();
    },

    //将值转化为弧度
    valToDeg(v) {
      let range = this.endDeg - this.startDeg;
      let val = (range / this.max) * v;
      if (this.isCounterClockWise && val != 0) val = 2 - val;
      let startDeg = this.isCounterClockWise
        ? 2 - this.startDeg
        : this.startDeg;
      return (startDeg + val) * Math.PI;
    },

    //设置渐变色
    setLinearGradient(color, ctx) {
      const grad = ctx.createLinearGradient(0, 0, 0, this.width);
      color.forEach((e, i) => {
        if (i == 0) {
          grad.addColorStop(0, e);
        } else if (i == color.length - 1) {
          grad.addColorStop(1, e);
        } else {
          grad.addColorStop((1 / color.length) * (i + 1), e);
        }
      });
      return grad;
    },

    // 弧度转化为对应坐标值
    DegToXY(deg) {
      let d = 2 * Math.PI - deg;
      return this.respotchangeXY({
        x: this.radius * Math.cos(d),
        y: this.radius * Math.sin(d),
      });
    },

    //中心坐标转化为canvas坐标
    respotchangeXY(point) {
      const spotchangeX = (i) => {
        return i + this.center;
      };
      const spotchangeY = (i) => {
        return this.center - i;
      };
      return {
        x: spotchangeX(point.x),
        y: spotchangeY(point.y),
      };
    },

    //节流函数
    throttle(func) {
      let previous = 0;
      return function () {
        let now = Date.now();
        let context = this;
        let args = arguments;
        if (now - previous > 10) {
          func.apply(context, args);
          previous = now;
        }
      };
    },

    //canvas坐标转化为中心坐标
    spotchangeXY(point) {
      const spotchangeX = (i) => {
        return i - this.center;
      };
      const spotchangeY = (i) => {
        return this.center - i;
      };
      return {
        x: spotchangeX(point.x),
        y: spotchangeY(point.y),
      };
    },

    // 将坐标点转化为弧度
    XYToDeg(lx, ly) {
      let adeg = Math.atan(ly / lx);
      let deg;
      if (lx >= 0 && ly >= 0) {
        deg = adeg;
      }
      if (lx <= 0 && ly >= 0) {
        deg = adeg + Math.PI;
      }
      if (lx <= 0 && ly <= 0) {
        deg = adeg + Math.PI;
      }
      if (lx > 0 && ly < 0) {
        deg = adeg + Math.PI * 2;
      }
      return deg;
    },

    //滑动开始
    touchStart(e) {
      if (this.lock) {
        return false;
      }
      const touches = e.mp.changedTouches[0] || e.changedTouches[0];

      let range = 10;
      let X = touches.x;
      let Y = touches.y;
      let P = this.P;

      let minX = P.x - this.sliderSize - range;
      let maxX = P.x + this.sliderSize + range;
      let minY = P.y - this.sliderSize - range;
      let maxY = P.y + this.sliderSize + range;
      if (minX < X && X < maxX && minY < Y && Y < maxY) {
        //判断是否按在在滑块上
        this.isDown = true;
      } else {
        this.isDown = false;
      }
    },

    //滑动
    touchMove(e) {
      if (!this.isDown) return;
      const touches = e.mp.changedTouches[0] || e.changedTouches[0];

      let evpoint = {};
      evpoint.x = touches.x;
      evpoint.y = touches.y;
      let point = this.spotchangeXY(evpoint);
      let deg = this.XYToDeg(point.x, point.y);
      deg = this.isCounterClockWise ? deg : Math.PI * 2 - deg;
      const radian = deg / Math.PI;
      let vals =
        ((radian -
          (radian > this.startDeg ? this.startDeg : -this.residueDeg)) /
          (this.endDeg - this.startDeg)) *
        this.max;

      if (vals > 100 || vals < 0) return;
      if (vals >= this.max) vals = this.max;
      if (vals <= 0) vals = 0;
      if (Math.abs(vals - this.val) > 10) return;
      this.animate = requestAnimationFrame(this.draw.bind(this, vals));
      if (this.val != Math.round(vals)) {
        this.val = Math.round(vals);
        this.$emit("change", this.val);
      }
    },

    //滑动结束
    touchEnd(e) {
      const _this = this;
      this.$emit("mouseUp", this.val);
      cancelAnimationFrame(_this.animate);
      this.isDown = false;
    },
  },
};
</script>

<style scoped></style>
