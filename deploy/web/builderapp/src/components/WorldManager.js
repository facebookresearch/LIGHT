import React from "react";
import CONFIG from "../config";
import {useAPI } from "../utils";
import {Button, Intent, Spinner} from "@blueprintjs/core";

function ListWorlds (props) {
    const { loading, result, reload } = useAPI(
      CONFIG,
      `/worlds/`
    );
    const data = result;
    if (!props.isOpen || data == undefined){
        return <></>;
    }else if (loading){
        return <Spinner intent={Intent.PRIMARY} />;
    }else{
        return(
        <>
            <table
                data-testid="world-review"
                style={{ width: "100%" }}
                className="bp3-html-table bp3-html-table-condensed bp3-interactive"
            >
            <thead>
            <tr>
                <th>World ID</th>
                <th>World Name</th>
                <th>Load</th>
                <th>Delete</th>
            </tr>
            </thead>
            <tbody>
                {data.map((d) => (
                    <React.Fragment key={d.id}>
                    <tr
                        data-testid="tr-review"
                        style={{
                        background: undefined
                        }}
                    >
                        <td>{d.id}</td>
                        <td>
                        <strong>{d.name}</strong>
                        </td>
                        <td>
                        <Button
                            intent={Intent.SUCCESS}
                            type="submit"
                            onClick={() => {props.toggleOverlay(!props.isOpen);
                                            props.state.getWorld(d.id); }
                                    }
                        >
                            Load
                        </Button>
                        </td>
                        <td>
                        <Button
                            intent={Intent.DANGER}
                            type="submit"
                            onClick={() => {props.state.deleteWorld(d.id); 
                                            props.toggleOverlay(!props.isOpen); 
                                            props.toggleOverlay(props.isOpen);}
                                    }
                        >
                            Delete
                        </Button>
                        </td>
                    </tr>
                    </React.Fragment>
                    ))}
            </tbody>
            </table> 
        </>); 
    }
}
  
export default ListWorlds;
