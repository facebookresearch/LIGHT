//GetWindowDimensions - function that will get and format dimensions of window for purposes of adding them to a components state.
const GetWindowDimensions = () =>{
    const { innerWidth: width, innerHeight: height } = window;
    return {
        width,
        height
    };
}

export default GetWindowDimensions;
