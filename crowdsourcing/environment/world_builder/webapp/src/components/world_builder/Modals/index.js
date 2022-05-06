/* REACT */
import React from 'react';
/* REDUX */
import {useAppDispatch, useAppSelector} from '../../app/hooks';
import {
  setModal,
} from "../../features/modal/modal-slice";
/* STYLES */
import './styles.css';
/* BOOTSTRAP COMPONENTS */
import Modal from 'react-bootstrap/Modal'
/* CUSTOM COMPONENTS */
// MODALS
import CopyModal from "./CopyModal";
import DeleteModal from "./DeleteWorldModal";
import DownloadModal from "./DownloadWorldModal";
import ShareModal from "./ShareWorldModal";
import CreateWorldModal from "./CreateWorldModal"
import CreateFromFileWorldModal from "./CreateWorldFromFileWorldModal";
import CreateFromScratchWorldModal from "./CreateFromScratchWorldModal"
import CreatePreGenWorldModal from "./CreatePreGenWorldModal"


const ModalContent = ({modalType})=>{
    switch (modalType) {
        case "download":
          return <DownloadModal/>
        case 'share':
          return <ShareModal/>
        case 'copy':
          return <CopyModal/>
        case 'delete':
          return <DeleteModal/>
        case 'createNewWorld':
          return <CreateWorldModal/>
          case 'preGenWorld':
            return <CreatePreGenWorldModal/>
          case 'uploadWorld':
            return <CreateFromFileWorldModal/>
          case 'fromScratchWorld':
            return <CreateFromScratchWorldModal/>
        default:
          return <div/>
    }
}

const ModalContainer = ()=> {
  /* ----REDUX STATE---- */
  //MODALS;
  const showModal = useAppSelector((state) => state.modal.showModal);
  const modalType = useAppSelector((state) => state.modal.modalType);
  /* ----REDUX ACTIONS---- */
  // REDUX DISPATCH FUNCTION
  const dispatch = useAppDispatch();
  //MODALS
  const closeModal = ()=> {
    dispatch(setModal({showModal:false, modalType:""}))
  };
    return (
        <Modal
          show={showModal}
          onHide={closeModal}
        >
            <ModalContent
                modalType={modalType}
            />
        </Modal>
    );
}

export default ModalContainer;
