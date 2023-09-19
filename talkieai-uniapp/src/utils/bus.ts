export default class EventBus {
  constructor() {
    (this as any).events = {};
  }
  emit(eventName: any, data: any) {
    if ((this as any).events[eventName]) {
      (this as any).events[eventName].forEach(function (fn: any) {
        fn(data);
      });
    }
  }
  on(eventName: any, fn: any) {
    (this as any).events[eventName] = (this as any).events[eventName] || [];
    (this as any).events[eventName].push(fn);
  }

  off(eventName: any, fn: any) {
    if ((this as any).events[eventName]) {
      for (let i = 0; i < (this as any).events[eventName].length; i++) {
        if ((this as any).events[eventName][i] === fn) {
          (this as any).events[eventName].splice(i, 1);
          break;
        }
      }
    }
  }
}
