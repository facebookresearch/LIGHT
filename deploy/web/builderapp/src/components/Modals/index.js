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
import DeleteModal from "./DeleteModal";
import DownloadModal from "./DownloadModal";
import ShareModal from "./ShareModal";


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