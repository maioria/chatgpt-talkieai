import {ref} from 'vue'
import service from '../service'
export function useIndexInfo () {
    const myIndexInfo = ref<any>('');
    const loading = ref<boolean>(false)
    const getIndexInfo = async () => {
        loading.value = true;
        const data = await service.sendOpt({url: '/index/indexInfo', method: 'get'}) as any;
        loading.value = false;
        myIndexInfo.value = data?.code;
    }
    return {
        myIndexInfo,
        getIndexInfo,
        loading
    }

}